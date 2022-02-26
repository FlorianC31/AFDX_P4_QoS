#!/usr/bin/env python3

import os
import sys
import platform

from scapy.all import sniff, Packet, Ether, StrFixedLenField, XByteField, IntField, bind_layers, BitField


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


def packet_filter(packet):
    return packet[Ether].type == 0x666

def PacketHandler(packet):
    if packet_filter(packet):
        packet.show()


def main():
    bind_layers(Ether, Afdx, type=0x666)
    if platform.system() == 'Linux':
        iface_name = get_wireless_interface()
    else:
        iface_name = input("Please enter wireless interface name: ")

    #ethernet
    #iface_name ="enp4s0f2"
    print(f"Monitoring AFDX packets on interface: {iface_name}")
    sniff(iface=iface_name, prn=PacketHandler)


if __name__ == '__main__':
    main()
