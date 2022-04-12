## Coded by I.A as part of ITP EMS 2021-2022
##
## this script logs the traffic using tcpdump Command
## both live through a graphic interface and also saves the traffic to txt files
## example for running the code : python3 sniffer.py interface1_vlid
## a folder named with current date & time is created and within it files
## containing the full traffic captured during the execution of the script
## PS : MAXIMUM 8 Nodes, for more change template of GUI tkinter and variable lengths

# librairies
from datetime import datetime
import logging
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from tkinter import StringVar, Label, RAISED, Text, Scrollbar
from shutil import which

try:
    import Tkinter as tk  # Python 2
except ImportError:
    import tkinter as tk  # Python 3


# getting nodes to listen to sent within arguments
nodes_to_listen = sys.argv
cmds = [None]*(len(sys.argv)-1)
vls = [None]*(len(sys.argv)-1)
for i in range(len(sys.argv)):
    if i != 0:
    	interface = str(sys.argv[i]).split("_")[0]
    	vl = int(str(sys.argv[i]).split("_")[1])
    	if vl < 10:
    		vl = "03:00:00:00:00:0"+str(vl)
    	else:
    		vl = "03:00:00:00:00:"+str(vl)
    	cmds[i-1] = "tcpdump -i "+ interface + " ether host " + vl + " -A"
    	vls[i-1] = vl

# main class
class ShowProcessOutputDemo:

    # initialisation function
    def __init__(self, root,cmd,tex,file_name,vl):

        self.root = root
        self.tex = tex
        self.cmd = cmd
        self.vl = vl
        self.file_name = file_name

        # start subprocess
        self.proc = Popen(cmd, shell=True,stdout=PIPE, stderr=STDOUT)

        # show subprocess' stdout in GUI
        self.root.createfilehandler(
            self.proc.stdout, tk.READABLE, self.read_output)

    def parse_data(self, data_to_parse):
   		data_parsed = ""
   		for line in data_to_parse.split("\n"):
   			if line[0:16] != "tcpdump: verbose" and line[0:9] != "listening"  and not("(invalid)" in line[0:16]):
   				if " " in line[0:16]:
   					data_parsed = data_parsed + line[0:15] + "," + self.vl + ","
   				elif ":" in line[0:14]:
   					data_parsed = data_parsed + line[0:14] + "\n" 
   		return data_parsed
    
    # function that will be executed when tcpdump command returns a result
    def read_output(self, pipe, mask):
        """Read subprocess' output, pass it to the GUI."""
        data = os.read(pipe.fileno(), 1 << 20)
        if data:  # check if data is piped in
            self.tex.insert(tk.END,data.strip(b'\n').decode() + '\n')
            self.tex.see("end")
            file_handle = open(self.file_name, "a")
            data_to_write = data.decode().replace("\r\n", "\n").replace("\n	0x0000"," - ")
            data_to_write_parsed = self.parse_data(data_to_write)
            file_handle.write(data_to_write_parsed)
            file_handle.close()

# initialisation of graphic user interface
root = tk.Tk()
root.geometry("1000x1000")
root.title('afdx sniffer')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
# root.columnconfigure(2, weight=1)
# root.columnconfigure(3, weight=1)

# creating folder for saving the result log file
now = datetime.now()
current_time = now.strftime("%H_%M_%S")
path = os.getcwd()
result_folder = path + "/results_"+current_time
os.mkdir(result_folder)

# creating text areas in the GUI and linking each text area to a certain Command
# that is executed for a certain node
var = [None]*len(sys.argv)
label = [None]*len(sys.argv)
tex = [None]*len(sys.argv)

for i in range(len(sys.argv)-1):
    var[i] = StringVar()
    var[i].set(nodes_to_listen[i+1])

    label[i] = Label(root, textvariable=var[i], relief=RAISED, height=1)
    label[i].grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)

    tex[i] = Text(master=root,height=5, width=150)
    tex[i].config(font=('Arial', 8, 'bold', 'italic'))
    tex[i].grid(column=1, row=i, sticky=tk.W, padx=5, pady=5)

    scrollbar = Scrollbar(root, orient='vertical', command=tex[i].yview, width = 16)
    scrollbar.grid(column=1, row=i, sticky='NSE')

    tex[i]['yscrollcommand'] = scrollbar.set

    f = result_folder+"/"+str(sys.argv[i+1])
    app = ShowProcessOutputDemo(root,cmds[i],tex[i],f,vls[i])

root.mainloop()
# info('exited')
