#eth0 is using onboard ethernet

#setup eth1 port using usb dongle
echo "Renaming usb dongle to eth1"
ifconfig enxb0a7b92ccddf down
ip link set enxb0a7b92ccddf name eth1
ifconfig eth1 up

#setup eth2 port using usb dongle
echo "Renaming usb dongle to eth2"
ifconfig enxb0a7b92ccb43 down
ip link set enxb0a7b92ccb43 name eth2
ifconfig eth2 up

#create veth2 to be used with br3
echo "Creating veth2 to be used with bridge br3"
ip link add dev veth2 type veth peer name veth2-1
ip link set dev veth2   address 00:04:00:00:20:00
ip link set dev veth2-1 address 00:04:00:00:20:10
ip link set dev veth2 up
ethtool -K veth2 tx off
ethtool -K veth2-1 tx off

#create bridge br2 and connect eth0 to it
echo "Creating bridge br2"
ip netns exec gigport ip link set veth1-1 netns 1
ip link set dev veth1-1 up
brctl addbr br2
brctl setageing br2 0
ip link set dev br2 up

echo "Connecting eth0 to br2"
ip link set eth0 promisc on
brctl addif br2 eth0
brctl addif br2 veth1-1

#connect eth1 to br0
echo "Connecting eth1 to br0 and disconnecting wlan0" 
brctl delif br0 wlan0
brctl addif br0 eth1

#create bridge3
echo "creating bridge br3 and connecting it to veth2 and eth2" 
ip link set dev veth2-1 up
brctl addbr br3
brctl setageing br3 0
ip link set dev br3 up

#connect devices to br3
brctl addif br3 eth2
brctl addif br3 veth2-1


echo "setup a switch with 3 ports"
echo "don't froget to setup the t4p4s configuration accordingly"
brctl show

