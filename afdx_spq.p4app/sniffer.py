# example for running the code : python3 sniffer.py h1 h2 h3 s1-eth1 s2-eth3 s1-eth2 s1-eth3
#  PS : MAXIMUM 8 Nodes, for more change template of GUI tkinter and variable lengths

from datetime import datetime
import logging
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from tkinter import *
try:
    import Tkinter as tk
except ImportError: # Python 3
    import tkinter as tk

nodes_to_listen = sys.argv
cmds = [None]*(len(sys.argv)-1)
for i in range(len(sys.argv)):
	if i != 0:
		if sys.argv[i][0] == 'h':
			cmds[i-1] = "./p4app exec m "+str(sys.argv[i])+" tcpdump -U"
		if sys.argv[i][0] == 's':
			cmds[i-1] = "./p4app exec tcpdump -i "+str(sys.argv[i])

class ShowProcessOutputDemo:
    def __init__(self, root,cmd,tex,file_name):

        self.root = root
        self.tex = tex
        self.cmd = cmd
        self.file_name = file_name

        # start subprocess
        self.proc = Popen(cmd, shell=True,stdout=PIPE, stderr=STDOUT)

        # show subprocess' stdout in GUI
        self.root.createfilehandler(
            self.proc.stdout, tk.READABLE, self.read_output)

    def read_output(self, pipe, mask):
        """Read subprocess' output, pass it to the GUI."""
        data = os.read(pipe.fileno(), 1 << 20)
        if data:  # check if data is piped in
        	self.tex.insert(tk.END,data.strip(b'\n').decode() + '\n')
        	self.tex.see("end")
        	file_handle = open(self.file_name, "a")
        	file_handle.write(data.strip(b'\n').decode() + '\n')
        	file_handle.close()

root = tk.Tk()
root.geometry("1000x1000")
root.title('afdx sniffer')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)

now = datetime.now()
current_time = now.strftime("%H_%M_%S")
path = os.getcwd()
result_folder = path + "/results_"+current_time
os.mkdir(result_folder)

var = [None]*8
label = [None]*8
tex = [None]*8
for i in range(8):
	if i < len(sys.argv)-1:
		var[i] = StringVar()
		var[i].set(nodes_to_listen[i+1])
		label[i] = Label( root, textvariable=var[i], relief=RAISED )
		label[i].grid(column=int(i/2), row=(2*i)%4, sticky=tk.W, padx=5, pady=5)
	tex[i] = Text(master=root,height=20)
	tex[i].config(font=('Arial', 8, 'bold', 'italic'))
	tex[i].grid(column=int(i/2), row=(2*i+1)%4, sticky=tk.W, padx=5, pady=5)
	scrollbar = Scrollbar(root, orient='vertical', command=tex[i].yview)
	scrollbar.grid(column=int(i/2), row=(2*i+1)%4, sticky='NSE')
	tex[i]['yscrollcommand'] = scrollbar.set
	if i< len(sys.argv)-1:
		f = result_folder+"/"+str(sys.argv[i+1])
		app = ShowProcessOutputDemo(root,cmds[i],tex[i],f)

root.mainloop()

info('exited')
