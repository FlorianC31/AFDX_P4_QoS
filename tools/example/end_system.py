# Script to send VL packet from p4app host
# This script should be direclty launched with the check_VL.sh scripts

from scapy.all import Ether, Raw, sendp, BitField, bind_layers
import sys
import random, string
import time
import platform


class Afdx(Packet):
    name = "Afdx"
    fields_desc = [
        BitField("dstConst", 0x3000000, 32),
        BitField("dstVL", 0, 16),
        BitField("srcMac_cst", 0x20000, 24),
        BitField("srcMac_addr", 0x0, 24),
        BitField("etherType", 0x666, 16)
    ]

def convert_data(data_num):
    data_temp = str(data_num).zfill(10);
    return (data_temp[0:2]+":"+data_temp[2:4]+":"+data_temp[4:6]+":"+data_temp[6:8]+":"+data_temp[8:10]);

def get_packet(VL_dst,Src_const,data_int):
    return Ether(dst=VL_dst,src=Src_const, type = 0x666)/Raw(load=convert_data(data_int))
	
# Get arguments
name, iface_name, npackets, *_ = sys.argv
vl_bag_array = sys.argv[2:]
npackets = int(npackets)

#bind layers to AFDX
bind_layers(Ether, Afdx, type=0x666)

Src_const = "02:00:00"
VL_dsts = []
bags = []

for vl_bag in vl_bag_array:
    vl = int(vl_bag.split("_")[0])
    if vl < 10:
    	VL_dsts.append("03:00:00:00:00:0" + str(vl))
    else:
    	VL_dsts.append("03:00:00:00:00:" + str(vl))
    bags.append(int(vl_bag.split("_")[1])/1000)

packets = [[None for j in range(npackets)] for i in range(len(vl_bag_array))]
for i in range(len(vl_bag_array)):
    for j in range(npackets):
    	packets[i][j] = get_packet(VL_dsts[i],Src_const,j)
    	
data_numeric = [0 for i in range(len(vl_bag_array))]
send_times = [time.time() for i in range(len(vl_bag_array))]

while True:
    for i in range(len(vl_bag_array)):
    	if data_numeric[i] < npackets:
            if time.time() >= send_times[i] + bags[i]:
                #print(str(i)+" :  send time : "+str(send_times[i]) + " // bag : "+str(bags[i]))
                sendp(packets[i][data_numeric[i]], iface = iface_name)
                send_times[i] = time.time()
                print("Vl : "+VL_dsts[i]+ " || data : "+ str(data_numeric[i]) + " || time : "+ str(send_times[i]) )
                data_numeric[i] = data_numeric[i] + 1
