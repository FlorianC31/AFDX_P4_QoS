## Coded by I.A as part of ITP EMS 2021-2022
##
##

from datetime import datetime
import numpy
import matplotlib.pyplot as plt
import scipy.stats

departure_logs = ["parsed_h1","parsed_h2","parsed_h3"]
arrival_log = "parsed_h17"
vls_to_analyse = ["03:00:00:00:00:01","03:00:00:00:00:02","03:00:00:00:00:03"]
format_string = "%H:%M:%S.%f" # time format needed for comparison
n_bins = 100 # number of histrogram bins
histrogram_data = [[] for vl in vls_to_analyse]
indx = -1
for vl in vls_to_analyse: # loop through all vls
    indx = indx + 1
    total_passing_through_switch_time = 0
    number_of_packets = 0
    for departure_log in departure_logs: # loop through departure_logs
        f_departure = open(departure_log, "r") # open file for current departure_log
        f_departure_lines = f_departure.readlines()
        for dep_line in f_departure_lines: # loop through lines of departure_log
            if dep_line[16:33] == vl: # check if current line match the current vl being checked
                f_arrival = open(arrival_log, "r") # open arrival_log file
                f_arrival_lines = f_arrival.readlines()
                for arrival_line in f_arrival_lines:  # loop through lines of arrival_log
                    if arrival_line[16:33] == vl and dep_line[34:48]==arrival_line[34:48]: # check matching vls & matching packet departure vs arrival
                        departure_time_text = dep_line[0:15] # extract switch entry time from departure_line
                        arrival_time_text = arrival_line[0:15] # extract switch departure time from arrival_line
                        departure_time = datetime.strptime(departure_time_text, format_string)
                        arrival_time = datetime.strptime(arrival_time_text, format_string)
                        # Get the interval between two datetimes as timedelta object
                        diff = arrival_time - departure_time
                        # Get the interval in microseconds
                        diff_in_micro_secs = diff.total_seconds() * 1000000
                        # Calculations needed for average
                        total_passing_through_switch_time = total_passing_through_switch_time + diff_in_micro_secs
                        number_of_packets = number_of_packets + 1
                        # Calculations needed for histrogram plotting
                        histrogram_data[indx].append(diff_in_micro_secs)
    average_time = int(total_passing_through_switch_time / number_of_packets)
    print("Vl : "+ str(vl) + " || average end-end delay : "+str(average_time)+" us")

# histogram plotting
for i in range(len(vls_to_analyse)):
    n, bins = numpy.histogram(numpy.array(histrogram_data[i]), n_bins)# plt.hist(x=numpy.array(histrogram_data[i]), bins=n_bins, color='#0504aa',alpha=0.7, rwidth=0.85)
    vals = n/sum(n)*100
    plt.plot(bins[:-1], vals)
plt.legend(vls_to_analyse)
plt.xlabel("end to end delay")
plt.ylabel("% of VL packets")
plt.title("end-to-end delays comparison")
plt.show()
