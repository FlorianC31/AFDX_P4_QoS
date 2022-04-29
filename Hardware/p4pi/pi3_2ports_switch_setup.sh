#setup onboard ethernet to eth0
#this step is only needed for raspberry pi 3, do not do this for raspberry pi 4
echo "setup onboard ethernet to eth0"
ifconfig enxb827eb664f43 down
ip link set enxb827eb664f43 name eth0
ifconfig eth0 up

#setup eth1 port using usb dongle
echo "Renaming usb dongle to eth1"
ifconfig enxb0a7b92ccbff down
ip link set enxb0a7b92ccbff name eth1
ifconfig eth1 up

#need to test if this next line solves a probable issue
#p4pi-setup

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


echo "setup a switch with 2 ports"
echo "don't froget to setup the t4p4s configuration accordingly"
brctl show


