## Coded by I.A as part of ITP EMS 2021-2022
##
## this script takes the log files for the switch ingress and egress ports
## example : s1-eth1, s1-eth2,....
## And, return a formated version (saved in file named parsed_name-of-input-log,
## example: parsed_s1-eth1) these resulting files could be used in log_analyser.property
## for analysis

import sys

logfile_to_parse = str(sys.argv[1])
f2 = open("parsed_"+logfile_to_parse, "w")
with open(logfile_to_parse) as f:
    lines = f.readlines()
    for line in lines:
        if len(line) > 200:
            data_to_write = line.replace(" 02:00:00:00:00:00 (oui Unknown) > ",",");
            index = data_to_write.find('Flags [Command]', 0)
            if index != -1:
                data_to_write = data_to_write[0:index-71]+","+data_to_write[index+73:];
            print(data_to_write)
            f2.write(data_to_write)
f2.close()
