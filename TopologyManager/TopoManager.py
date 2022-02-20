import os
from queue import PriorityQueue
import sys
from shutil import which

PACKET_SIZE = 64
TABLE_NAME = "afdx_table"
ACTION_NAME = "Check_VL"
MC_DUMP = True
DEFAULT_BAG = 64
DEFAULT_PRIO = 1

_help = """
Automatic creation p4app files with given topology file
Launching command: 
python3 TopoManager.py <input_topo_file> [<destination path>]
Destination path is current directory by default
Input : 
- Input topology file (see 'input_topo.txt' as example)
Outputs:
- topo.txt file (to be added in the p4app package)
- commands_x.txt file : switch table for each switch (to be added in the p4app package)
- check_VLx.sh files to be executed after running p4app to check the VLs
"""

class BagError(Exception):
    """Exception raised when the defined BAG is not a power of 2 """

    def __init__(self, vl_id, bag_value):
        self.message = "ERROR: For " + vl_id + ", the BAG=" + bag_value + " is not a power of 2."
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
        print('VL_ID:', self.id)
        for path in self.paths:
            print("-", path, "- BAG:", self.bag, "- Priority:", self.priority)


class Switch:
    def __init__(self, switch_id, distant_entity):
        """ Class containing the switches Data
            Each entity connected to the switch is attributed to a port number from 1.
            Therefore, all the the entity are stored in the 'ports' list :
            - the ports[0] is '-'
            - then, ports[port_id] = connected entity name (switch or host)
            The connection dict contains the connexion between ingress port and outgress ports list for each VL
        """

        self.id = switch_id
        self.ports = ['', distant_entity]  # Creation of the port list with the first entity
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
        print('Switch:', self.id)
        i = 0
        for port in self.ports[1:]:
            i += 1
            print("- " + self.id + "-eth" + str(i) + ": " + port)

        for connect in self.connections:
            outgress_list = "/".join(map(str, self.connections[connect]['outgress_port']))
            print(connect + ": eth" + str(self.connections[connect]['ingress_port']) + "->eth" + outgress_list)


class Topology:
    def __init__(self, topo_filename):
        """ Class containing all the switches, host, VL and physical connections of the input topology """

        self.connections = []  # Physical connections
        self.vls = {}
        self.switches = {}
        self.hosts = []

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

    def read_link(self, data_line):
        """ Reading links in topo input file """

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

    def create_switch_connections(self):
        """ For each switch : a in/out port connection is created for each VL passing by this switch """

        for switch in self.switches:
            for vl in self.vls:
                self.switches[switch].add_connection(self.vls[vl])

    def write_topo_file(self, filename):
        """ Creation of the topo file to be given in input in the p4app package """

        with open(filename, 'w') as file:
            file.write("switches " + str(len(self.switches)) + '\n')
            file.write("hosts " + str(len(self.hosts)) + '\n')

            for connect in self.connections:
                file.write(str(' '.join(connect)) + '\n')

    def write_switch_cmd_files(self):
        """ Creation of the command.txt file for each switch for the p4app input package """

        for switch in self.switches:
            with open("commands_" + switch[1:] + ".txt", 'w') as file:
                node_handle = 0
                group_id = 1
                for vl_connect in self.switches[switch].connections:
                    priority=self.vls[vl_connect].priority
                    vl_id = str(vl_connect[2:])  # Removing 'VL' label and keeping only the number 
                    ingress_port = str(self.switches[switch].connections[vl_connect]['ingress_port'])
                    outgress_ports = " ".join(map(str, self.switches[switch].connections[vl_connect]['outgress_port']))

                    mc_mgrp_create_line = ("mc_mgrp_create", str(group_id), '\n')
                    table_add_line = ("table_add",
                                      TABLE_NAME,
                                      ACTION_NAME,
                                      ingress_port,
                                      vl_id,
                                      "=>",
                                      str(PACKET_SIZE),
                                      str(group_id),
                                      str(priority),
                                      '\n')
                    mc_node_create_line = ("mc_node_create", str(node_handle), outgress_ports, '\n')
                    mc_node_associate_line = ("mc_node_associate", str(group_id), str(node_handle), '\n')

                    file.write(" ".join(mc_mgrp_create_line))
                    file.write(" ".join(table_add_line))
                    file.write(" ".join(mc_node_create_line))
                    file.write(" ".join(mc_node_associate_line))
                    file.write('\n')

                    node_handle += 1
                    group_id += 1

                if MC_DUMP:
                    file.write("mc_dump\n")

    def write_check_files(self):
        """ Writing of checking script for each VL. These scripts perform 2 actions :
        - Calling sniffing script with all the host and switch ports crossed by the current VL
        - Sending a packet on the source host of the current VL """

        for vl in self.vls:
            with open("check_" + vl + ".sh", 'w') as file:
                # Call sniffing script with all the host and switch ports crossed by the current VL
                output_line = ["python3", "sniffer.py"]
                for path in self.vls[vl].paths:
                    for entity in path:
                        if entity[0] == 's':  # if the entity is a switch
                            # Ingress interface
                            previous_entity = path[path.index(entity) - 1]
                            ingress_port = self.switches[entity].ports.index(previous_entity)
                            ingress = entity + "-eth" + str(ingress_port)
                            if ingress not in output_line:
                                output_line.append(ingress)

                            # Outgress interface
                            next_entity = path[path.index(entity) + 1]
                            outgress_port = self.switches[entity].ports.index(next_entity)
                            outgress = entity + "-eth" + str(outgress_port)
                            if outgress not in output_line:
                                output_line.append(outgress)

                        else:  # if it's a host
                            if entity not in output_line:
                                output_line.append(entity)
                file.write(" ".join(output_line[:10]))
                file.write(" &\n")
                host = self.vls[vl].paths[0][0]

                # Send a packet on the source host of the current VL
                if which('p4app') is not None:
                    # if the p4app has been added in the /usr/local/bin/ folder
                    p4app_cmd = "p4app"
                else:
                     # else, p4app has to be in the folder where the check_VLx.sh files are launched
                    p4app_cmd = "./p4app"
                file.write(p4app_cmd + " exec m " + host + " python ../tmp/send_afdx_packet.py " + vl + ' ' + host + ' ' + self.vls[vl].bag)

    def print(self):
        """ Print the topology details:
        - Physical connections
        - VLs details
        - Switches details
        """

        print("Physical connections :", self.connections)
        for vl in self.vls:
            self.vls[vl].print_paths()

        for switch in self.switches:
            self.switches[switch].print()


if __name__ == "__main__":
    try:
        script_name, topo_input_file, *_ = sys.argv
        dest_path = sys.argv[-1] if sys.argv[-1] != topo_input_file else '.'

        new_topo = Topology(topo_input_file)  # Creation of the topology structure
        new_topo.print()  # Print the topology in console

        os.chdir(dest_path)
        new_topo.write_topo_file("topo.txt")  # Write the topo file for p4app
        new_topo.write_check_files()  # Write all the check_vl.sh files to check the VL
        new_topo.write_switch_cmd_files()  # Write de command.txt table for each switch (for p4app)

    except ValueError:
        print("ERROR: missing argument" + _help)

    except BagError as e:
        print(e)
