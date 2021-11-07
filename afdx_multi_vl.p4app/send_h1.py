from scapy.all import Ether, Raw, sendp
import sys
import random, string
import time

def randomword(max_length):
    length = random.randint(1, max_length)
    return ''.join(random.choice(string.lowercase) for i in range(length))

VL_dst = "03:00:00:00:00:01"
Src_const = "02:00:00"
data = "12:34:56:78:90" # data = randomword(2)

p = Ether(dst=VL_dst,src=Src_const)/Raw(load=data)
print ' ----------------- I M ALIVE'
print p.show()

while True:
    sendp(p, iface = 'h1-eth0')
    time.sleep(1/10)
