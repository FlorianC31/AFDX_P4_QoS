# Example Description

The 'input_topo_afdx.txt' file describes the topology presented in the figure below.

![image](https://user-images.githubusercontent.com/72257044/165805722-89b10d72-983d-4ad3-92ad-302653a75de8.png)

- one 4-ports PC switch with T4P4S
- one 2-ports Raspberry 3 switch with P4PI (the original ethernet port with 1 additional ethernet/USB dongle)
- one 3-ports Raspberry 4 switch with P4PI (the original ethernet port with 2 additional ethernet/USB dongles)
- one 5-ports PC to emulate 5 end-system hosts


# Topology files modification

In order to launch this example on physical Network, the 'input_topo_afdx.txt' file needs to be modified in order to configure the Ethernet Card names according with the ones on the PC used to emulate the 5 end-systems:
```shell
h1,PC1,enp4s0
h2,PC1,enp5s0f0
h3,PC1,enp5s0f1
h4,PC1,enp5s4f0
h5,PC1,enp5s4f1
```



# Files Generation

Launch the followind command to automatically generate input files:
```shell
python3 TopoManager.py input_topo.txt t4p4s generated_files
```

Launch it again with p4pi parameter instead of t4p4s to generate switch 2 and 3 files for Raspberry format:
```shell
python3 TopoManager.py input_topo.txt p4pi generated_files
```

This notice is printed in the terminal by TopoManager.py:
- 'switch1_t4p4s.txt' file has to be included in the afdx.p4 files for t4p4s.
- 'switch2_p4pi.txt' and 'switch3_p4pi.txt' files have to be included in the afdx.p4 files for p4pi.
- 'analysis_topo.txt' has to be given into input for 'analyser.py' script.
- 'sniffer_h1_PC1_enp4s0.sh' has to be launched on PC1 to monitor all packets exiting and arriving on h1.
- 'sniffer_h5_PC1_enp5s4f1.sh' has to be launched on PC1 to monitor all packets exiting and arriving on h5.
- 'sniffer_h2_PC1_enp5s0f0.sh' has to be launched on PC1 to monitor all packets exiting and arriving on h2.
- 'sniffer_h3_PC1_enp5s0f1.sh' has to be launched on PC1 to monitor all packets exiting and arriving on h3.
- 'sniffer_h4_PC1_enp5s4f0.sh' has to be launched on PC1 to monitor all packets exiting and arriving on h4.
- 'sniffer_PC1_all_hosts.sh' has to be launched on PC1 to monitor all packets exiting and arriving on all hosts of the PC.
- 'end_system_h1_PC1_enp4s0.sh' has to be launched on PC1 to send packets on all VL from h1 on interface enp4s0.
- 'end_system_h2_PC1_enp5s0f0.sh' has to be launched on PC1 to send packets on all VL from h2 on interface enp5s0f0.
- 'end_system_h3_PC1_enp5s0f1.sh' has to be launched on PC1 to send packets on all VL from h3 on interface enp5s0f1.
- 'end_system_h4_PC1_enp5s4f0.sh' has to be launched on PC1 to send packets on all VL from h4 on interface enp5s4f0.
- 'sender_PC1_all_VL.sh' has to be launched on PC1 to send packets on all VL from this PC.
- 'switch1_p4pi.txt', 'switch2_t4p4s.txt' and 'switch3_t4p4s.txt' are not used and can be deleted.

The script print also the detail of each Switch.
This is very helpful to wire the physical network (what host/switch on what port).



# Include switch table in AFDX.p4

Copy paste the content of each switch.txt file into corresponding AFDX.p4 files at line 69, in :
```P4
control MyIngress(inout headers hdr,inout metadata meta,inout standard_metadata_t standard_metadata) {
    table afdx_table_port {
        const entries = {
            ...
        }
    }
}
```


# Launch switches

- See /Hardware/p4pi/ to launch switches on Raspberry
- See /Hardware/t4p4s/ to launch switches on PC


# Send and monitor packets

- Use 'send_PC1_all_VL.sh' on PC1 to launched all VL on PC1
- Use 'sniffer_PC1_all_hosts.sh' on PC1 to monitor all exiting/entering packets


# Analysis of the results

Copy .pcap files near the analyser.py python script along with the file 'analysis_topo.txt' following the example given in /Tools/README.md
then launch the logs : 
```shell
python3 analyser.py analysis_topo.txt
```
