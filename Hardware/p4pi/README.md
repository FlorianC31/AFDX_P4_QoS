# To Run P4 Switch on Raspberry Pi:

To setup the P4PI platform on Raspberry Pi, start by reading the From_Raspberry_PI_to_P4_Switch text file.

For a detailed guide to setup the AFDX (or any other type of P4 program) on the P4PI instance, read the following documents:
	P4PI_AFDX_Switch.txt
	P4PI_General_Wiki.txt
	For Raspberry PI model 3B, read the P4PI_Raspberry_Pi_3_Notes.txt

#Quick guide to run AFDX P4 program on Raspberry Pi:
You will need at least 1 usb to ethernet dongle to test with 2 ethernet ports
or
You can test with ethernet and wifi (but this is not recommended)

1 - Download P4PI https://github.com/p4lang/p4pi/releases and setup your raspberry pi.

2 - Copy the afdx_p4pi.p4 into the /root/t4p4s/examples folder

3 - Adapt and run one of the two helper scripts
	pi4_switch_setup_3_ports.sh 
	pi3_2ports_switch_setup.sh
   /!\ Don't forget to adapt the interface names to what you have /!\


4 - Add the following line to /root/t4p4s/examples.cfg:
afdx_p4pi			    arch=dpdk hugepages=1024 model=v1model smem vethmode pieal piports

5 - According to the number of ports you want to use, modify the following lines in /root/t4p4s/opts_dpdk.cfg:

pieal   -> ealopts += -c 0xc -n 4 --no-pci --vdev net_pcap0,rx_iface_in=veth0,tx_iface=veth0,tx_iface=veth0 --vdev net_pcap1,rx_iface_in=veth1,tx_iface=veth1,tx_iface=veth1 ;--vdev net_pcap2,rx_iface_in=veth2,tx_iface=veth2,tx_iface=veth2

;to add ports declare them in previous line and change the bitmask, 0x3 means ports 0 and 1 are active, 0x07 means ports 0, 1 and 2 are active
piports -> cmdopts += -p 0x7 --config "\"(0,0,2)(1,0,3)\""

6 - Compile and run the switch:
		1- sudo su
		2- echo afdx_p4pi > /root/t4p4s-switch
		3- systemctl restart t4p4s.service
			OR
		3- systemctl stop t4p4s.service
		   systemctl start t4p4s.service
OR run in debug mode:
		systemctl stop t4p4s.service
		cd /root/t4p4s
		./t4p4s.sh :afdx_p4pi p4rt verbose dbg

