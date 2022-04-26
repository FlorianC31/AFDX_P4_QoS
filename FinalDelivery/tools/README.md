# TopoManager.py

The objective of this tool is to generate automaticaly complexe AFDX topology for p4app (Mininet), p4pi (Raspberry) or t4p4s (Linux PC).

## Launching command: 
```shell
python3 TopoManager.py <input_topo_file> <output_platform> [<destination path>]
```
Automatic creation switch command and VL check files with given topology file.

Destination path is current directory by default.

## Inputs: 
- Input topology file (see 'input_topo.txt' as example)
- Platform type: 'p4app' for mininet, 'p4pi' for Raspberry, 't4p4s' for PC
- [optional] destination path for the output files (default value, same repertory as the script) 

## Outputs:
- commands_x.txt : switch table for each switch
- check VL file : sniffer + packet sender for each VL
- topo.txt file (only for p4app) : to be added in the p4app package

---

## Environement:

> AFDX general parameters:
- `MAX_PACKET_SIZE` AFDX max packet size (default `64`)
- `ACTION_NAME` P4 : Name of the action function (default `"Check_VL"`)
- `DEFAULT_BAG` AFDX default BAG (default `64`)

> t4p4s (Linux PC) & p4pi (Raspberry) parameters:
- `AFDX_PREFIX` AFDX prefix (default `"03:00:00:00:00"`)
- `NB_PACKETS` Default number of packets to be send in test (default `1000`)
- `SENDER_SCRIPT_NAME` Name of the Python script used to send packer (default `"end_system.py "`)

> p4app (Mininet) parameters:
- `TABLE_NAME` AFDX table name (default `"afdx_table"`)
- `DEFAULT_PRIO` Default priority (if not defined in the input topo txt file) (default `1`)
- `MININET_SENDER_SCRIPT` Name of the Python script used to send packets in Mininet p4app package (default `"send_afdx_packet.py"`)
- `MININET_SNIFFER_SCRIPT` Name of the Python script used to monitor packets in Mininet (default `"sniffer_mininet.py"`)
- `MININET_MC_DUMP` Show the tables in mininet (default `True`)
- `P4APP_PRIORITY` Enable priority management (default `False`)


# analyser.py



# end_system.py

Only for linux hardware (t4p4s / p4pi).
For Mininet and p4app, the script send_afdx_packet.py has to be used (or included in the p4app package).
See /QoS/NO_QOS.p4app/send_afdx_packet.py