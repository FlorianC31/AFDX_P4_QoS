# Implementation of a Real-Time Ethernet with Quality-of-Service mechanisms

## Abstract

This project has been performed as an Integrated Team Project of the Embedded Systems Advanced Master from ISAE-Supaéro & INP-Enseeiht.
See "/Reports" folder for more details.


## OUR MISSIONS

### AFDX P4 HARDWARE IMPLEMENTATION
Implement AFDX network switching capabilities on real hardware: PC (Linux stations) along with raspberry PI3 and PI4.


### QUALITY OF SERVICE MECHANISMS
Add quality of service mechanisms such as SPQ, WRR and optionally DRR to the P4 based AFDX switches.



## OUR SOLUTION

### AFDX ON PC
Using the library DPDK and the compiler T4P4S, a solution was implemented to give a Linux PC the capability to act as an AFDX switch using the language P4.

![image](https://user-images.githubusercontent.com/72257044/165796410-cb7a1a92-70fc-4407-978b-c701b46f9d6a.png)




### AFDX ON RASPBERRY PI 3 & PI 4
Using the network data plane P4PI, both versions of Raspberry pi3 and pi4 can be turned into functional AFDX switches.



### QOS FOR AFDX
A Static Priority Queue along with pseudo Weighted Round Robin algorithms were implemented on P4 using the software p4 compilation target behavioral model v2 (BMV2).



## GROWTH HIGHLIGHTS
Airbus, the market leader in AFDX deployment as of 2022, does not adopt a quality-of-service mechanism. This study served as a proof of concept for the viability of incorporating such processes into the AFDX airborne network, potentially adding an additional layer of security by prioritizing time-sensitive flows (such as flight control) above less crucial ones (infotainment for example).


# Tutorial

## Simulation With Mininet & p4app

### Step 1

In the folder 'Simulation/BENCHMARK_NO_QOS/'

Use the input_topo.txt file as an input for with the Tools/TopoManager.py script with the following command:
```shell
python3 TopoManager.py input_topo.txt p4app output_folder
```
The following files will be generated in the 'output_folder' directory and will need to be placed in the p4app package:
- topo.txt (containing topology data for Mininet)
- commands_X.txt for each switch (with X is the switch number)

The following files will also be generated in the 'output_folder' to be used at step 4 and 5:
- send_all_packets.sh -> To be called in Linux terminal to send pakets on all Virutal Links
- analysis_topo.txt -> File to be given in input for the analyser.py script (see step4).
- sniffer.sh -> To be called in Linux terminal to dump packets into pcap files


### Step 2

The p4app package 'example.p4app' needs to contain:
- topo.txt file generated at step 1
- commands_X.txt files generated at step 1
- P4 file with the script behaviour (for example afdx.p4)
- p4app.json containing usefull data for p4app
- send_afdx_packet.py which be used at step 4 by send_all_packets.sh script on each Mininet host
- topo.py which will be call by Mininet to build topology from topo.txt file

See 'Simulation/BENCHMARK_NO_QOS/BENCHMARK.p4app' for p4app package example.

### Step 3

Launch p4app with the following command :
```shell
p4app run example.p4app
```
/!\ if p4app script is not install in the user bin but it located direclty in the working directory, this command has to be used :
```shell
./p4app run example.p4app
```

### Step 4
Launch the packet sniffing using tcpdump via the bash script sniffer.sh
```shell
./sniffer.sh
```

### Step 5
to send packets for all the VLs we use the send_all_packets.sh bash script:
```shell
./send_all_packets.sh
```
Copy .pcap files from /tmp/p4appp_logs near the analyser.py python script along with a file (named for example input_topo_for_analysis.txt) describing the topology for the analyser.py following the example given in /main/Tools/README.md
then launch the logs : 
```shell
python3 analyser.py input_topo_for_analysis.txt
```

## Run Switch on Hardware (Linux PC or Raspberry)
See /Hardware/example/README.md

