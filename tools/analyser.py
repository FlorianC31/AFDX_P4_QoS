## Coded by I.A as part of ITP EMS 2021-2022
##
##

from datetime import datetime
import numpy
import matplotlib.pyplot as plt
import scipy.stats
from scapy.all import *

def read_pcap(file_name):
	parser = PcapReader(file_name)
	lines = []
	for p in parser:
	    payload = p.load[0:14].decode()
	    dst = p.dst
	    time = str(p.time)
	    line_to_add = time+","+dst+","+payload
	    lines.append(line_to_add)
	return lines

departure_logs = []
arrival_logs = []
vls_to_analyse = []
vls_to_plot = [] # used as legend for the plot

# Get arguments
name, analysis_topo_file = sys.argv
analysis_topo_handler = open(analysis_topo_file, "r")

# Construct pcap file & VL names 
for line in analysis_topo_handler.readlines():
    split_line = line.strip().split(",")
    vl = int(split_line[0])
    if vl < 10:
    	dst = "03:00:00:00:00:0" + str(vl)
    	vls_to_analyse.append(dst)
    	vls_to_plot.append("VL"+str(vl))
    else:
    	dst = "03:00:00:00:00:" + str(vl)
    	vls_to_analyse.append(dst)
    	vls_to_plot.append("VL"+str(vl))
    
    departure = split_line[1]+".pcap"
    departure_logs.append(departure)
    
    arrival = split_line[2]+".pcap"
    arrival_logs.append(arrival)

n_bins = 100 # number of histrogram bins
histrogram_data = [[] for vl in vls_to_analyse]
for i in range(len(vls_to_analyse)): # loop through all vls
    total_end_to_end_delay = 0
    number_of_packets = 0
    departure_log = read_pcap(departure_logs[i])
    arrival_log = read_pcap(arrival_logs[i])
    # print to console : 
    for departure_packet in departure_log: # loop through departure packets for the VL[i]
        if departure_packet.strip().split(",")[1] == vls_to_analyse[i]:
            for arrival_packet in arrival_log:  # loop through lines of arrival packets for the VL[i]
                if arrival_packet.strip().split(",")[1] == vls_to_analyse[i] and departure_packet.strip().split(",")[2]==arrival_packet.strip().split(",")[2]: # check matching vls & matching packet departure vs arrival
                    departure_time = float(departure_packet.strip().split(",")[0]) # extract departure time
                    arrival_time = float(arrival_packet.strip().split(",")[0]) # extract arrival time
                    # Get the interval in microseconds
                    end_to_end_delay_in_micro_secs = (arrival_time - departure_time) * 1000
                    # Calculations needed for average
                    total_end_to_end_delay = total_end_to_end_delay + end_to_end_delay_in_micro_secs
                    number_of_packets = number_of_packets + 1
                    # Calculations needed for histrogram plotting
                    histrogram_data[i].append(end_to_end_delay_in_micro_secs)
    if number_of_packets > 0:
    	average_time = end_to_end_delay_in_micro_secs / number_of_packets
    	print("Vl : "+ vls_to_plot[i] + " || average end-end delay : "+str(average_time)+" ms")
    else:
    	print("No packet in logs for Vl : "+vls_to_plot[i])
    print(vls_to_plot[i] + " Analyzed | total Number of packets : " + str(number_of_packets)) 

# histogram plotting
for i in range(len(vls_to_analyse)):
    n, bins = numpy.histogram(numpy.array(histrogram_data[i]), n_bins)
    vals = n/sum(n)*100
    plt.plot(bins[:-1], vals)

# show plots
plt.legend(vls_to_plot)
plt.xlabel("end to end delay")
plt.ylabel("% of VL packets")
plt.title("end-to-end delays comparison (ms)")
plt.show()
