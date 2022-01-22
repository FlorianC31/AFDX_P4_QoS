## Coded by I.A as part of ITP EMS 2021-2022
##
##

from datetime import datetime
import numpy
import matplotlib.pyplot as plt
import scipy.stats

ingress_logs = ["parsed_s1-eth1","parsed_s1-eth2","parsed_s1-eth3"]
engress_log = "parsed_s1-eth4"
vls_to_analyse = ["03:00:00:00:00:01","03:00:00:00:00:02","03:00:00:00:00:03"]
format_string = "%H:%M:%S.%f" # time format needed for comparison
n_bins = 10 # number of histrogram bins
histrogram_data = [[] for vl in vls_to_analyse]
indx = -1
for vl in vls_to_analyse: # loop through all vls
    indx = indx + 1
    total_passing_through_switch_time = 0
    number_of_packets = 0
    for ingress_log in ingress_logs: # loop through ingress_log
        f_ingress = open(ingress_log, "r") # open file for current ingress log
        ingress_lines = f_ingress.readlines()
        for i_line in ingress_lines: # loop through lines of ingress log
            if i_line[16:33] == vl: # check if current line match the current vl being checked
                f_egress= open(engress_log, "r") # open egress log file
                engress_lines = f_egress.readlines()
                for e_line in engress_lines:  # loop through lines of egress log
                    if e_line[16:33] == vl and i_line[34:48]==e_line[34:48]: # check matching vls & matching packet ingress vs egress
                        entry_time_text = i_line[0:15] # extract switch entry time from ingress line
                        departure_time_text = e_line[0:15] # extract switch departure time from egress line
                        entry_time = datetime.strptime(entry_time_text, format_string)
                        departure_time = datetime.strptime(departure_time_text, format_string)
                        # Get the interval between two datetimes as timedelta object
                        diff = departure_time - entry_time
                        # Get the interval in microseconds
                        diff_in_micro_secs = diff.total_seconds() * 1000000
                        # Calculations needed for average
                        total_passing_through_switch_time = total_passing_through_switch_time + diff_in_micro_secs
                        number_of_packets = number_of_packets + 1
                        # Calculations needed for histrogram plotting
                        histrogram_data[indx].append(diff_in_micro_secs)
    average_time = int(total_passing_through_switch_time / number_of_packets)
    print("Vl : "+ str(vl) + " || average switching time : "+str(average_time)+" ms")

# histogram plotting
for i in range(len(vls_to_analyse)):
    n, bins = numpy.histogram(numpy.array(histrogram_data[i]), n_bins)# plt.hist(x=numpy.array(histrogram_data[i]), bins=n_bins, color='#0504aa',alpha=0.7, rwidth=0.85)
    vals = n/sum(n)
    plt.plot(bins[:-1], vals)
plt.legend(vls_to_analyse)
plt.xlabel("switching delay")
plt.ylabel("% of VL packets")
plt.title("Switching delays comparison")
plt.show()
