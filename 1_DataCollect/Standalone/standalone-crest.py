from rq import Queue
from worker import conn

from time import sleep
from utils import send_crest_requset, RepeatedTimer, scan_port

import argparse

# bind and show a key press event with tkinter
from tkinter import *

import csv
standaloneWriter = csv.writer(open("./standalone.csv", 'w'))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip", type=str, default="192.168.0.2",
	help="IP address to get CREST data")

ap.add_argument("-p", "--port", type=int, default=8080,
	help="IP address to get CREST data")
args = vars(ap.parse_args())

ip = args["ip"]
q = Queue(connection=conn)
def main():
    global standaloneWriter
    result = q.enqueue(send_crest_requset, ip + ':' + str(args["port"]),'standalone',{})

print("starting...")

root = Tk()
prompt = '      Press s to start, q to quit      '
label1 = Label(root, text=prompt, width=len(prompt), bg='yellow')
label1.pack()

def key(event):
    stop = True
    global rt
    if event.char == 's':
        if scan_port(ip,args["port"]) == True and stop == True:
            rt = RepeatedTimer(0.1, main) # it auto-starts, no need of rt.start()
            label1.config(text='Getting Data From CREST, Press q to quit.')
            stop = False
    elif event.char == 'q':
        rt.stop()
        label1.config(text='Stop Getting Data From CREST, Press s to start.')
        stop = True
    

root.bind_all('<Key>', key)

root.mainloop()