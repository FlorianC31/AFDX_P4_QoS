TOPO_FILE = "input_topo.txt"
PACKET_SIZE = 64
TABLE_NAME = "afdx_table"
ACTION_NAME = "Check_VL"
MC_DUMP = True


class VirtualLink:
    def __init__(self, data_line):
        self.id = data_line[0]
        self.paths = []
        self.add_path(data_line)

    def add_path(self, data_line):
        if type(data_line[-1]) != str:
            self.paths.append(data_line[1:])
        else:
            self.paths.append(data_line[1:-1])

    def print_paths(self):
        print('')
        print('VL_ID:', self.id)
        for path in self.paths:
            print("-", path)


class Switch:
    def __init__(self, switch_id, distant_entity):
        self.id = switch_id
        self.ports = ['', distant_entity]
        self.connections = {}

    def add_port(self, distant_entity):
        self.ports.append(distant_entity)

    def add_connection(self, vl):
        for path in vl.paths:
            if self.id in path:
                ingress_entity = path[path.index(self.id) - 1]  # get the previous entity in the path
                outgress_entity = path[path.index(self.id) + 1]  # get the next entity in the path
                ingress_port = self.ports.index(ingress_entity)
                outgress_port = self.ports.index(outgress_entity)

                if vl.id not in self.connections:  # if the VL is not existing on the switch
                    self.connections[vl.id] = {'ingress_port': ingress_port, 'outgress_port': [outgress_port]}
                else:  # if it already exists (multicast VL), the outgress port is added in the outgress ports list
                    self.connections[vl.id]['outgress_port'].append(outgress_port)

    def print(self):
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

        self.connections = []
        self.vls = {}
        self.switches = {}
        self.hosts = []

        self.read_input_file(topo_filename)
        self.create_switch_connections()

    def read_input_file(self, topo_filename):

        with open(topo_filename, 'r') as topo_file:
            line = topo_file.readline()

            # Reading of links
            while line[:7] != "--start" and line != '':
                line = topo_file.readline()
            line = topo_file.readline()  # Jump the line "--start"

            while line[:6] != "--stop" and line != '':
                self.read_link(line)
                line = topo_file.readline()

            # Reading of virtual links
            while line[:7] != "--start" and line != '':
                line = topo_file.readline()
            line = topo_file.readline()  # Jump the line "--start"

            while line[:6] != "--stop" and line != '':
                self.read_vls(line)
                line = topo_file.readline()

    def create_switch_connections(self):
        for switch in self.switches:
            for vl in self.vls:
                self.switches[switch].add_connection(self.vls[vl])

    def read_entity(self, switch_data, i):
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

    def read_link(self, data_line):
        data = data_line.split(',')
        self.connections.append(data[0:2])

        self.read_entity(data, 0)
        self.read_entity(data, 1)

    def read_vls(self, data_line):
        data = data_line.split(',')

        # if the virtual link is not existing yet, it's created
        if data[0] not in self.vls:
            self.vls[data[0]] = VirtualLink(data)

        else:  # else, the VL is completed with the new path
            self.vls[data[0]].add_path(data)

    def write_topo_file(self, filename):
        with open(filename, 'w') as file:
            file.write("switches " + str(len(self.switches)) + '\n')
            file.write("hosts " + str(len(self.hosts)) + '\n')

            for connect in self.connections:
                file.write(str(' '.join(connect)) + '\n')

    def write_switch_cmd_files(self):
        for switch in self.switches:
            with open("commands_" + switch[1:] + ".txt", 'w') as file:
                node_handle = 0
                groupe_id = 1
                for connect in self.switches[switch].connections:
                    vl_id = str(connect[2:])
                    ingress_port = str(self.switches[switch].connections[connect]['ingress_port'])
                    outgress_ports = " ".join(map(str, self.switches[switch].connections[connect]['outgress_port']))

                    mc_mgrp_create_line = ("mc_mgrp_create", str(groupe_id), '\n')
                    table_add_line = ("table_add",
                                      TABLE_NAME,
                                      ACTION_NAME,
                                      ingress_port,
                                      vl_id,
                                      "=>",
                                      str(PACKET_SIZE),
                                      str(groupe_id),
                                      '\n')
                    mc_node_create_line = ("mc_node_create", str(node_handle), outgress_ports, '\n')
                    mc_node_associate_line = ("mc_node_associate", str(groupe_id), str(node_handle), '\n')

                    file.write(" ".join(mc_mgrp_create_line))
                    file.write(" ".join(table_add_line))
                    file.write(" ".join(mc_node_create_line))
                    file.write(" ".join(mc_node_associate_line))
                    file.write('\n')

                    node_handle += 1
                    groupe_id += 1

                if MC_DUMP:
                    file.write("mc_dump\n")

    def write_check_files(self):
        for vl in self.vls:
            with open("check_" + vl + ".sh", 'w') as file:
                ligne = ["python3", "sniffer.py"]
                for path in self.vls[vl].paths:
                    for entity in path:
                        if entity[0] == 's':  # if the entity is a switch
                            # Ingress interface
                            previous_entity = path[path.index(entity) - 1]
                            ingress_port = self.switches[entity].ports.index(previous_entity)
                            ingress = entity + "-eth" + str(ingress_port)
                            if ingress not in ligne:
                                ligne.append(ingress)

                            # Outgress interface
                            next_entity = path[path.index(entity) + 1]
                            outgress_port = self.switches[entity].ports.index(next_entity)
                            outgress = entity + "-eth" + str(outgress_port)
                            if outgress not in ligne:
                                ligne.append(outgress)

                        else:  # if it's a host
                            if entity not in ligne:
                                ligne.append(entity)
                file.write(" ".join(ligne[:10]))
                file.write(" &\n")
                host = self.vls[vl].paths[0][0]
                file.write("p4app exec m " + host + " python ../tmp/send_afdx_packet.py " + vl + ' ' + host)

    def print(self):
        print(self.connections)
        for vl in self.vls:
            self.vls[vl].print_paths()

        for switch in self.switches:
            self.switches[switch].print()


if __name__ == "__main__":
    new_topo = Topology(TOPO_FILE)
    new_topo.print()
    new_topo.write_topo_file("topo.txt")
    new_topo.write_check_files()
    new_topo.write_switch_cmd_files()
