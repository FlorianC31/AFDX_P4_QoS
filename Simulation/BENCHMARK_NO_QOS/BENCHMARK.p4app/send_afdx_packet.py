# Script to send VL packet from p4app host
# This script should be direclty launched with the check_VL.sh scripts

from scapy.all import Ether, Raw, sendp
import sys
import random, string
import time

def convert_data(data_num):
    data_temp = str(data_num).zfill(10);
    ADDED_DATA_SIZE = 0;
    return (data_temp[0:2]+":"+data_temp[2:4]+":"+data_temp[4:6]+":"+data_temp[6:8]+":"+data_temp[8:10])+"*"*ADDED_DATA_SIZE;

# Get arguments
name, vl, host, bag = sys.argv

# packet data
if int(vl[2:]) < 10:
    VL_dst = "03:00:00:00:00:0" + vl[2:]
else:
    #VL_dst = "03:00:00:00:00:" + vl[2:]
    VL_dst = "03:00:00:00:00:" + str(hex(int(vl[2:]))).replace('x','')
Src_const = "02:00:00"
data_numeric = 0
p = Ether(dst=VL_dst,src=Src_const)/Raw(load=convert_data(data_numeric)) # construction of first packet with data = 0

# loop to send packets taking into account the BAG
send_time = time.time()
while data_numeric < 10000:
    time_t = time.time()
    # print(time_t)
    if time_t >= send_time + float(bag) / 1000:
        send_time = time_t
        sendp(p, iface = host + '-eth0', verbose = False)
        data_numeric = (data_numeric + 1) % 9999999999
        p = Ether(dst=VL_dst,src=Src_const)/Raw(load=convert_data(data_numeric))  # construction of new packet with incremental data value from 00:00:00:00:00 to 99:99:99:99:99
print('Sending packets on ' + vl + ' done.')
