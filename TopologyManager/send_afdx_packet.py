# Script to send VL packet from p4app host
# This script should be direclty launched with the check_VL.sh scripts

from scapy.all import Ether, Raw, sendp
import sys
import random, string
import time

# Get arguments
name, vl, host, bag = sys.argv

# packet data
VL_dst = "03:00:00:00:00:0" + vl[-1]
Src_const = "02:00:00"
data = "12:34:56:78:90" # data = randomword(2)

# construction of the packet
p = Ether(dst=VL_dst,src=Src_const)/Raw(load=data)
print(p.show())

# loop to send packets taking into account the BAG
send_time = time.time()
while True:
    time_t = time.time()
    if time_t >= send_time + bag / 1000:
        send_time = time_t
        sendp(p, iface = host + '-eth0')
