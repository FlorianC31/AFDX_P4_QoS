## Coded by C.F. as part of ITP EMS 2021-2022
##

import os
import sys
from shutil import which
str_getenv = lambda str, default="": os.getenv(str, default)
int_getenv = lambda str, default=0: int(os.getenv(str) or default)

# INFO : Params can be declared in Environmenent, or directly here under (second argument)

###################### AFDX general parameters #######################
# AFDX packet size
PACKET_SIZE = int_getenv('PACKET_SIZE', 64)

# P4 : Name of the action function
ACTION_NAME = str_getenv('ACTION_NAME', "Check_VL")

# AFDX default BAG
DEFAULT_BAG = int_getenv('DEFAULT_BAG', 64)


######### t4p4s (Linux PC) & p4pi (Raspberry) parameters #############
# AFDX prefix
AFDX_PREFIX = str_getenv('AFDX_PREFIX', "03:00:00:00:00")

# Default number of packets to be send in test
NB_PACKETS = int_getenv('NB_PACKETS', 1000)

# Name of the Python script used to send packer
SENDER_SCRIPT_NAME = str_getenv('SENDER_SCRIPT_NAME', "end_system.py ")


#################### p4app (Mininet) parameters ######################
# AFDX table name
TABLE_NAME = str_getenv('TABLE_NAME', "afdx_table")

# Default priority (if not defined in the input topo txt file)
DEFAULT_PRIO = int_getenv('DEFAULT_PRIO', 1)

# Name of the Python script used to send packets in Mininet p4app package
MININET_SENDER_SCRIPT = str_getenv('MININET_SENDER_SCRIPT', "send_afdx_packet.py")

# Name of the Python script used to monitor packets in Mininet
MININET_SNIFFER_SCRIPT = str_getenv('MININET_SNIFFER_SCRIPT', "sniffer_mininet.py")

# Show the tables in mininet
MININET_MC_DUMP = bool(int_getenv('MININET_MC_DUMP', True))

# Enable priority management
P4APP_PRIORITY = bool(int_getenv('P4APP_PRIORITY', False))


_help = """
Automatic creation switch command and VL check files with given topology file.
Launching command: 
python3 TopoManager.py <input_topo_file> <platform_type> [<destination path>]
Destination path is current directory by default
Inputs: 
- Input topology file (see 'input_topo.txt' as example)
- Platform type: 'p4app' for mininet, 'p4pi' for Raspberry, 't4p4s' for PC
- [optional] destination path for the output files (default value, same repertory as the script) 
Outputs:
- commands_x.txt : switch table for each switch
- check VL file : sniffer + packet sender for each VL
- topo.txt file (only for p4app) : to be added in the p4app package

Info:
- The script use several parameters which can be direclty modified in the script or as environment variable.
"""

def get_p4app_command():
    if which('p4app') is not None:
        # if the p4app has been added in the /usr/local/bin/ folder
        p4app_cmd = "p4app"
    else:
        # else, p4app has to be in the folder where the check_VLx.sh files are launched
        p4app_cmd = "./p4app"
    return p4app_cmd



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



class BagError(Exception):
    """Exception raised when the defined BAG is not a power of 2 """

    def __init__(self, vl_id, bag_value):
        self.message = "For " + vl_id + ", the BAG=" + bag_value + " is not a power of 2. Check input topo file."
        super().__init__(self.message)



class InputError(Exception):
    def __init__(self, msg):
        """Exception raised for input error"""
        self.message = msg
        super().__init__(self.message)



class VirtualLink:
    def __init__(self, data_line):
        """ Class containing the Virtual links Data """
        self.id = data_line[0]
        self.paths = []
        self.bag = DEFAULT_BAG
        self.priority = DEFAULT_PRIO
        self.add_path(data_line)
        self.check_bag()


    def add_path(self, data_line):
        """ Add the VL path details from the data line form topo input file.
         In case of multicast VL, there will be a path by destination host """

        if data_line[-2].isdecimal():
            # The two last arguments are decimal => BAG and priority are defined in input_topo.txt
            self.paths.append(data_line[1:-2])
            self.bag = data_line[-2]
            self.priority = data_line[-1]

        elif not data_line[-2].isdecimal() and data_line[-1].isdecimal() :
            # Only the last argument is decimal => only the BAG is defined in input_topo.txt
            self.paths.append(data_line[1:-1])
            self.bag = data_line[-1]
            self.priority = DEFAULT_PRIO
            
        else:
            # The last argument is not decimal => Neither the BAG nor the priority are defined in input_topo.txt
            self.paths.append(data_line[1:])
            self.bag = DEFAULT_BAG
            self.priority = DEFAULT_PRIO


    def check_bag(self):
        # check if the BAG is a power of 2
        if int(self.bag) & (int(self.bag) -1) != 0:
            raise BagError(self.id, self.bag)


    def print_paths(self):
        """ Print the VL details """

        print('')
        print(f"{bcolors.HEADER}{bcolors.BOLD}VL_ID:{bcolors.ENDC}", f"{bcolors.OKBLUE}" + self.id + f"{bcolors.ENDC}")
        for path in self.paths:
            print("-", path, "- BAG:", self.bag, "- Priority:", self.priority)



class Switch:
    def __init__(self, switch_id, distant_entity):
        """ Class containing the switches Data
            Each entity connected to the switch is attributed to a port number from 0.
            Therefore, all the the entity are stored in the 'ports' list :
                - ports[port_id] = connected entity name (switch or host)
            The connection dict contains the connexion between ingress port and outgress ports list for each VL
        """

        self.id = switch_id
        self.ports = [distant_entity]  # Creation of the port list with the first entity
        self.connections = {}  #


    def add_port(self, distant_entity):
        """ Addition of an entity in the port list """

        self.ports.append(distant_entity)


    def add_connection(self, vl):
        """ For a given VL and the current switch: Addition of connexions between ingress port and outgress ports list
        The outgress port is a list because it can contain several ports in case of multicast VL.
        """

        for path in vl.paths:
            if self.id in path:
                ingress_entity = path[path.index(self.id) - 1]  # get the ingress entity in the path
                outgress_entity = path[path.index(self.id) + 1]  # get the outgress entity in the path
                ingress_port = self.ports.index(ingress_entity)
                outgress_port = self.ports.index(outgress_entity)

                if vl.id not in self.connections:  # if the VL is not existing yet on the switch
                    self.connections[vl.id] = {'ingress_port': ingress_port, 'outgress_port': [outgress_port]}
                else:  # if it already exists (multicast VL), the outgress port is added in the outgress ports list
                    self.connections[vl.id]['outgress_port'].append(outgress_port)


    def print(self):
        """ Print the switches details:
        - Detail of entity (switch or host) connected of each switch port
        - Detail of the ingress / outgress ports connexion for each VL
        """

        print('')
        print(f"{bcolors.HEADER}{bcolors.BOLD}Switch:{bcolors.ENDC}", f"{bcolors.OKBLUE}" + self.id + f"{bcolors.ENDC}")
        print("- Ports list:", self.ports)
        i = 0
        for port in self.ports:
            print("- " + self.id + "-port" + str(i) + ": " + port)
            i += 1

        for connect in self.connections:
            outgress_list = "/".join(map(str, self.connections[connect]['outgress_port']))
            print(connect + ": port" + str(self.connections[connect]['ingress_port']) + "->port" + outgress_list)



class Topology:
    def __init__(self, topo_filename):
        """ Class containing all the switches, host, VL and physical connections of the input topology """

        self.connections = []  # Physical connections
        self.vls = {}
        self.switches = {}
        self.hosts = []
        self.mapping = {}

        self.read_input_file(topo_filename)
        self.create_switch_connections()


    def read_input_file(self, topo_filename):
        """ Reading and processing input topo file"""

        with open(topo_filename, 'r') as topo_file:
            line = topo_file.readline()

            # Reading of links
            while not line.startswith("--start") and line != '':
                line = topo_file.readline()
            line = topo_file.readline()  # Jump the line "--start"

            while not line.startswith("--stop") and line != '':
                self.read_link(line.strip())
                line = topo_file.readline()

            # Reading of virtual links
            while not line.startswith("--start") and line != '':
                line = topo_file.readline()
            line = topo_file.readline()  # Jump the line "--start"

            while not line.startswith("--stop") and line != '':
                self.read_vls(line.strip())
                line = topo_file.readline()

            # Reading of port mapping
            while not line.startswith("--start") and line != '':
                line = topo_file.readline()
            line = topo_file.readline()  # Jump the line "--start"

            while not line.startswith("--stop") and line != '':
                self.read_mapping(line.strip())
                line = topo_file.readline()


    def read_link(self, data_line):
        """ Reading links in topo input file
            Only the two first fields are taken into account
        """

        data = data_line.split(',')
        self.connections.append(data[0:2])

        self.read_entity(data, 0)
        self.read_entity(data, 1)


    def read_entity(self, switch_data, i):
        """ For each entity of the link line, store it in switch dict or host list """

        entity_id = switch_data[i]
        distant_entity = switch_data[1-i]

        if entity_id[0] == 's':  # check if the entity is a switch
            if entity_id not in self.switches:
                self.switches[entity_id] = Switch(entity_id, distant_entity)
            else:
                self.switches[entity_id].add_port(distant_entity)

        elif entity_id[0] == 'h':  # if it's a hots, it's added to the host list
            if entity_id not in self.hosts:
                self.hosts.append(entity_id)

        else:
            raise NameError("The entity in the links list has to start with 's' for swhitchs or 'h' for hosts")


    def read_vls(self, data_line):
        """ Read vls line from input topo file and store them in vls dict """

        data = data_line.split(',')

        # if the virtual link is not existing yet, it's created
        if data[0] not in self.vls:
            self.vls[data[0]] = VirtualLink(data)

        else:  # else, the VL is completed with the new path (in case of multicast VL)
            self.vls[data[0]].add_path(data)


    def read_mapping(self, data_line):
        """ Read port mapping line from input topo file and store the in mapping dict """

        data = data_line.split(',')
        # Creation of a dictionnary where the key is the host_name and the value is a tuple (PC_name, eth_interface_name)
        self.mapping[data[0]] = (data[1], data[2])


    def create_switch_connections(self):
        """ For each switch : a in/out port connection is created for each VL passing by this switch """

        for switch in self.switches:
            for vl in self.vls:
                self.switches[switch].add_connection(self.vls[vl])


    def check_mapping(self):
        """ checking if the port maipping has been correclty defined in the topo input file:
        - each host has to be defined
        - a tuple (PC_name,eth_interface_name) can be associated to only one host
        """

        # Check that each host is defined
        for host in self.hosts:
            if host not in self.mapping:
                raise InputError("The host " + host + " is not defined in the port mapping in input topo file.")

        # check there is not duplicated tuple (PC_name,eth_interface_name)
        flipped={}
        for key, value in self.mapping.items():
            if value not in flipped:
                flipped[value] = [key]
            else:
                flipped[value].append(key)

        duplicates = []
        for k in flipped:
            if len(flipped[k]) > 1:
                duplicates.append(str(k) + " defined on " + ", ".join(flipped[k]))

        if len(duplicates)>0:
            raise InputError("Some duplicate interfaces have been found in the port mapping in input topo file:\n" + "\n".join(duplicates))

        print('')
        print(f"{bcolors.HEADER}{bcolors.BOLD}Physical port mapping:{bcolors.ENDC}", self.mapping)


    def write_topo_file(self, filename):
        """ Creation of the topo file to be given in input in the p4app package """

        with open(filename, 'w') as file:
            file.write("switches " + str(len(self.switches)) + '\n')
            file.write("hosts " + str(len(self.hosts)) + '\n')

            for connect in self.connections:
                file.write(str(' '.join(connect)) + '\n')


    def write_switch_cmd_files_p4app(self):
        """ Creation of the command.txt file for each switch for the p4app input package """
        
        switch_list = []
        for switch in self.switches:
            switch_list.append("commands_"  + switch[1:] + ".txt")
            with open(switch_list[-1], 'w') as file:
                node_handle = 0
                group_id = 1
                for vl_connect in self.switches[switch].connections:
                    priority=self.vls[vl_connect].priority
                    vl_id = str(vl_connect[2:])  # Removing 'VL' label and keeping only the number 

                    # for p4app, ports have to be numbered from 1 instead of from 0: therefore +1 is added in the in/out ports numbers
                    ingress_port = str(self.switches[switch].connections[vl_connect]['ingress_port']+1)
                    outgress_ports = " ".join(map(str, [i + 1 for i in self.switches[switch].connections[vl_connect]['outgress_port']]))

                    mc_mgrp_create_line = ("mc_mgrp_create", str(group_id), '\n')
                    table_add_line = ["table_add",
                                    TABLE_NAME,
                                    ACTION_NAME,
                                    ingress_port,
                                    vl_id,
                                    "=>",
                                    str(MAX_PACKET_SIZE),
                                    str(group_id),
                                    str(priority),
                                    '\n']

                    # if the priority management is disable, the priority is removed from the line
                    if not P4APP_PRIORITY:
                        del table_add_line[-2]

                    mc_node_create_line = ("mc_node_create", str(node_handle), outgress_ports, '\n')
                    mc_node_associate_line = ("mc_node_associate", str(group_id), str(node_handle), '\n')

                    file.write(" ".join(mc_mgrp_create_line))
                    file.write(" ".join(table_add_line))
                    file.write(" ".join(mc_node_create_line))
                    file.write(" ".join(mc_node_associate_line))
                    file.write('\n')

                    node_handle += 1
                    group_id += 1

                if MININET_MC_DUMP:
                    file.write("mc_dump\n")

        if len(switch_list) > 0:
            print('')
            print(f"{bcolors.HEADER}{bcolors.BOLD}NOTICE (for output files):{bcolors.ENDC}")
            if len(switch_list) == 1:
                print(" - '" + "', '".join(switch_list) + "' file has to be included in the p4app package for Mininet.")
            else:
                print(" - '" + "', '".join(switch_list) + "' files have to be included in the p4app package for Mininet.")


    def write_switch_cmd_files_linux(self, platform_type):
        """ Creation of the command.txt file for each switch for the p4app input package
            Input : "platform_type"
        """

        switch_list = []
        for switch in self.switches:
            switch_list.append("switch" + switch[1:] + "_" + platform_type + ".txt")     
            with open(switch_list[-1], 'w') as file:
                node_handle = 0
                group_id = 1
                for vl_connect in self.switches[switch].connections:
                    priority=self.vls[vl_connect].priority
                    vl_id = str(vl_connect[2:])  # Removing 'VL' label and keeping only the number 

                    ingress_port = str(self.switches[switch].connections[vl_connect]['ingress_port'])   
                    outgress_port0 = str(self.switches[switch].connections[vl_connect]['outgress_port'][0])  # Take only the first port of the list (no multicasting)

                    if int(ingress_port)<10:
                        ingress_port="0x0" + ingress_port + "00"
                    else:
                        ingress_port="0x" + ingress_port + "00"

                    if int(vl_id)<10:
                        vl_id ="0x0" + vl_id
                    else:
                        vl_id="0x" + vl_id
                    if platform_type == 't4p4s':
                        vl_id = vl_id + "00"

                    line = "(" + ingress_port + ", " + vl_id + ") : " + ACTION_NAME + "(" + str(MAX_PACKET_SIZE) + ", " + outgress_port0 + ");"
                    file.write(line)
                    file.write('\n')

        if len(switch_list) > 0:
            print('')
            print(f"{bcolors.HEADER}{bcolors.BOLD}NOTICE (for output files):{bcolors.ENDC}")
            if len(switch_list) == 1:
                print(" - " + ", ".join(switch_list) + " file has to be included in the afdx.p4 file for " + platform_type + ".")
            else:
                print(" - " + ", ".join(switch_list) + " files have to be included in the afdx.p4 files for " + platform_type + ".")


    def write_check_files_p4app(self):
        """ Writing of checking script for each VL for p4app platform. These scripts perform 2 actions :
        - Calling sniffing script with all the host and switch ports crossed by the current VL
        - Sending a packet on the source host of the current VL """

        p4app_cmd = get_p4app_command()
        topo = []
        # Send a packet on a VL
        for vl in self.vls:
            with open("send_" + vl + ".sh", 'w') as file:
                host = self.vls[vl].paths[0][0]
                dest = self.vls[vl].paths[0][-1]
                topo.append(vl[2:] + ',' + host + ',' + dest)
                file.write(p4app_cmd + " exec m " + host + " python ../tmp/" + MININET_SENDER_SCRIPT + " " + vl + ' ' + host + ' ' + self.vls[vl].bag)
            print(" - 'send_" + vl + ".sh' has to be launched on a terminal (outside Mininet) to send poacket on " + vl + ".")

        # Send a packet on all VL at the same time
        with open("send_all_packets.sh", 'w') as file:
            file.write('echo "Sending packets on all VLs"')
            for vl in self.vls:
                host = self.vls[vl].paths[0][0]
                file.write(" & " + p4app_cmd + " exec m " + host + " python ../tmp/" + MININET_SENDER_SCRIPT + " " + vl + ' ' + host + ' ' + self.vls[vl].bag)
            file.write(' && bg')
            print(" - 'send_all_packets.sh' has to be launched on a terminal (outside Mininet) to send packets on all vl in the same time.")

        # Monitor VL on each host
        with open("sniffer.sh", 'w') as file:
            file.write('echo "Sniffing packets on all hosts"')
            for host in self.hosts:
                file.write(" & " +p4app_cmd + " exec m " + host + " tcpdump -w /tmp/p4app_logs/" + host + ".pcap")
            file.write(' && bg')
        print(" - 'sniffer.sh' has to be launched on a terminal (outside Mininet) to monitor all packets on all hosts and switch ports.")
        
        with open("analysis_topo.txt", 'w') as file:
            file.write("\n".join(topo))
        print(" - 'analysis_topo.txt' has to be given into input for 'analyser.py' script.")


    def write_check_files_linux(self):
        """ Writing of checking script for each VL for linux platforms (t4p4s and p4pi). These scripts perform 2 actions :
        - Calling sniffing script with all the host and switch ports crossed by the current VL
        - Sending a packet on the source host of the current VL """

        vl_dict = {}
        end_system_dict = {}

        # Get all the hosts and dest for each VL and generate analysis_topo.txt for analysis.py script
        with open("analysis_topo.txt", 'w') as file:
            for vl in self.vls:
                for path in self.vls[vl].paths:
                    end_system_host = path[0]
                    end_system_dest = path[-1]

                    if int(vl[2:]) > 9:
                        vl_str = " ether host " + AFDX_PREFIX + ":" + vl[2:]
                    else:
                        vl_str = " ether host " + AFDX_PREFIX + ":0" + vl[2:]

                    if end_system_host not in vl_dict:
                        vl_dict[end_system_host] = [vl_str]
                    else:
                        vl_dict[end_system_host].append(vl_str)

                    if end_system_dest not in vl_dict:
                        vl_dict[end_system_dest] = [vl_str]
                    else:
                        vl_dict[end_system_dest].append(vl_str)

                    vl_bag = vl[2:]  + '_' + str(self.vls[vl].bag)
                    if end_system_host not in end_system_dict:
                        end_system_dict[end_system_host] = [vl_bag]
                    else:
                        end_system_dict[end_system_host].append(vl_bag)
                file.write(vl[2:] + ',' + end_system_host + ',' + end_system_dest + '\n')
        print(" - 'analysis_topo.txt' has to be given into input for 'analyser.py' script.")

        # Write the sniffer files
        pc_sniffer = {}
        for end_system in vl_dict:
            pc, eth = self.mapping[end_system]

            with open("sniffer_" + end_system + "_" + pc + "_" + eth + ".sh", 'w') as file:
                line = "tcpdump -i " + eth + " or".join(vl_dict[end_system]) + " -w " + end_system + ".pcap"
                file.write(line)
                if pc in pc_sniffer:
                    pc_sniffer[pc].append(line)
                else:
                    pc_sniffer[pc] = [line]
            print(" - 'sniffer_" + end_system + "_" + pc  + "_" + eth + ".sh' has to be launched on " + pc + " to monitor all packets exiting and arriving on " + end_system + ".")

        with open("sniffer_" + pc + "_all_hosts.sh", 'w') as file:
            file.write("Sniffing all hosts on " + pc + ". & ")
            file.write(" & ".join(pc_sniffer[pc]))
            file.write(" && bg")
        print(" - 'sniffer_" + pc + "_all_hosts.sh' has to be launched on " + pc + " to monitor all packets exiting and arriving on all hosts of the PC.")

        # Write the sender files
        pc_sender = {}
        for end_system in end_system_dict:
            es_pc, es_eth = self.mapping[end_system]
            with open("end_system_" + end_system + "_" + es_pc + "_" + es_eth + ".sh", 'w') as file:
                line = "python3 " + SENDER_SCRIPT_NAME + " " + es_eth + " " + str(NB_PACKETS) + " " + " ".join(end_system_dict[end_system])
                file.write(line)
                if pc in pc_sender:
                    pc_sender[pc].append(line)
                else:
                    pc_sender[pc] = [line]
            print(" - 'end_system_" + end_system + "_" + es_pc + "_" + es_eth + ".sh' has to be launched on " + es_pc + " to send packets on all VL from " + end_system + " on interface " + es_eth + ".")
        
        with open("sender_" + pc + "_all_VL.sh", 'w') as file:
            file.write("Sending all VL from " + pc + ". & ")
            file.write(" & ".join(pc_sender[pc]))
            file.write(" && bg")
        print(" - 'sender_" + pc + "_all_VL.sh' has to be launched on " + es_pc + " to send packets on all VL from this PC.")


    def print(self):
        """ Print the topology details:
        - Physical connections
        - VLs details
        - Switches details
        """

        print(f"{bcolors.HEADER}{bcolors.BOLD}Physical connections:{bcolors.ENDC}", self.connections)

        for vl in self.vls:
            self.vls[vl].print_paths()

        for switch in self.switches:
            self.switches[switch].print()



def check_platform_type(platform_type):
    """ check if the output type is well defined (1, 2 or 3) only"""
    if platform_type not in ('p4app', 'p4pi', 't4p4s'):
        raise InputError("platform_type=" + platform_type + " - The output type of the write_switch_cmd_files has to be 'p4app', 'p4pi' or 't4p4s'")



if __name__ == "__main__":
    try:
        script_name, topo_input_file, platform_type, *_ = sys.argv
        if len(sys.argv) == 4:
            dest_path = sys.argv[3]
            try:
                os.makedirs(dest_path)
            except FileExistsError:
                pass
        else:
            dest_path = '.'

        check_platform_type(platform_type)

        new_topo = Topology(topo_input_file)  # Creation of the topology structure
        new_topo.print()  # Print the topology in console

        os.chdir(dest_path)

        if platform_type == 'p4app':
            new_topo.write_switch_cmd_files_p4app()  # Write de command.txt table for each switch
            new_topo.write_topo_file("topo.txt")  # Write the topo file for p4app
            new_topo.write_check_files_p4app()
        else:
            new_topo.check_mapping()  # Check the consistency of the port mapping
            new_topo.write_switch_cmd_files_linux(platform_type)  # Write de command.txt table for each switch
            new_topo.write_check_files_linux()

    except ValueError:
        print(f"{bcolors.FAIL}ERROR: missing argument{bcolors.ENDC}" + _help)

    except BagError as e:
        print(f"{bcolors.FAIL}INPUT BAG ERROR: {bcolors.ENDC}", e)

    except InputError as e:
        print(f"{bcolors.FAIL}INPUT ERROR: {bcolors.ENDC}", e)
