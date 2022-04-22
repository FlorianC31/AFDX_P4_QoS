# Script to send VL packet from p4app host
# This script should be direclty launched with the check_VL.sh scripts

from scapy.all import Ether, Raw, sendp
import sys
import random, string
import time


def convert_data(data_num):
    data_temp = str(data_num).zfill(10);
    return (data_temp[0:2]+":"+data_temp[2:4]+":"+data_temp[4:6]+":"+data_temp[6:8]+":"+data_temp[8:10])+ "*"*1450;

# Get arguments
name, vl, host, bag = sys.argv

# packet data
VL_dst = "03:00:00:00:00:0" + vl[-1]
Src_const = "02:00:00"
data_numeric = 0
p = Ether(dst=VL_dst,src=Src_const)/Raw(load=convert_data(data_numeric)) # construction of first packet with data = 0

# loop to send packets taking into account the BAG
send_time = time.time()
while True:
    time_t = time.time()
    if time_t >= send_time + int(bag) / 1000:
        send_time = time_t
        sendp(p, iface = host + '-eth0')
        data_numeric = (data_numeric + 1) % 9999999999
        p = Ether(dst=VL_dst,src=Src_const)/Raw(load=convert_data(data_numeric))  # construction of new packet with incremental data value from 00:00:00:00:00 to 99:99:99:99:99
