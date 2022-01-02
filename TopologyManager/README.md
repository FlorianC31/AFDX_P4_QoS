The objective of this tool is to generate automaticaly complexe AFDX topology for p4app.

Launching command: 
```shell
python3 TopoManager.py <input_topo_file> [<destination path>]
```
Destination path is current directory by default

Input : 
- Input topology file (see 'input_topo.txt' as example)

Outputs:
- topo.txt file (to be added in the p4app package)
- commands_x.txt file : switch table for each switch (to be added in the p4app package)
- check_VLx.sh files to be executed after running p4app to check the VLs
