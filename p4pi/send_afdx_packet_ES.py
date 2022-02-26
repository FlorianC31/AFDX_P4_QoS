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

def get_wireless_interface():
    """
    Get defult wireless interface
    """
    for device_name in os.listdir('/sys/class/net'):
        if os.path.exists(f'/sys/class/net/{device_name}/wireless'):
            return device_name
    print("Can't find WiFi interface")
    sys.exit(1)

#DST_ADDR = "10:04:00:00:10:10"
VL_dst = "03:00:00:00:00:02"
Src_const = "02:00:00"
data = "12:34:56:75:99" # data = randomword(2)

#bind layers to AFDX
bind_layers(Ether, Afdx, type=0x666)

#get the wirless interface
if platform.system() == 'Linux':
    iface_name = get_wireless_interface()
else:
    iface_name = input("Please enter wireless interface name: ")
print(f"Using interface: {iface_name}")

# construction of the packet
p = Ether(dst=VL_dst,src=Src_const, type = 0x666)/Raw(load=data)
print(p.show())
#ethernet
iface_name ="enp4s0f2"

# loop to send packets taking into account the BAG
sendp(p, iface = iface_name)
#send_time = time.time()
#while True:
#    time_t = time.time()
#    if time_t >= send_time + 10:
#        send_time = time_t
#        sendp(p, iface = iface_name)
