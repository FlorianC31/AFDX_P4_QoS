The objective of this tool is to generate automaticaly complexe AFDX topology for p4app (Mininet), p4pi (Raspberry) or t4p4s (Linux PC).

Launching command: 
```shell
python3 TopoManager.py <input_topo_file> <output_platform> [<destination path>]
```
Automatic creation switch command and VL check files with given topology file.

Destination path is current directory by default.

Inputs: 
- Input topology file (see 'input_topo.txt' as example)
- Platform type: 'p4app' for mininet, 'p4pi' for Raspberry, 't4p4s' for PC
- [optional] destination path for the output files (default value, same repertory as the script) 

Outputs:
- commands_x.txt : switch table for each switch
- check VL file : sniffer + packet sender for each VL
- topo.txt file (only for p4app) : to be added in the p4app package
