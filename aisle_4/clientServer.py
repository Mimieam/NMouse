#!/usr/bin/python
# -*- coding: latin-1 -*-

import socket
import threading
import time
from queue import Queue

import zmq

print("Current libzmq version is %s" % zmq.zmq_version())
print("Current  pyzmq version is %s" % zmq.__version__)

class Server(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self, args=(queue,))
        self.ctx = zmq.Context()
        self.q = queue
    
    def setup_listening_socket(self):
        self.listener = self.ctx.socket(zmq.SUB)
        self.listener.setsockopt_string(zmq.SUBSCRIBE, "HERE")
    
    def setup_talking_socket(self):
        self.talker = self.ctx.socket(zmq.ROUTER) 
        self.talker.bind('tcp://*:5556')

    def run(self):
        self.setup_listening_socket()
        self.setup_talking_socket()
        
        while True:
            msg = "hello"
            self.talker.send_string("%s" % msg)
            time.sleep(1)
            


        talker.close()
        listener.close()
        self.ctx.term()

if __name__ == "__main__":
    q = Queue()
    print (q)
    Serv = Server(q)
    Serv.run()
# context = zmq.Context()
# socket = context.socket(zmq.SUB)

# print("Collecting updates from weather server…")
# socket.connect("tcp://localhost:5556")

# topic = 'HERE' 

# # subscribe to messaged PREFIXED with zipfilter
# socket.setsockopt_string(zmq.SUBSCRIBE, topic)

# # Process 5 updates
# total_temp = 0

# while True:
#     recv = socket.recv_string()
#     print(string)
#     uid, xPos, yPos = string.split()
#     xPos = int(xPos)
#     yPos = int(yPos)
#     # print('The current pointer position is {0}'.format((xPos, yPos)))
#     # time.sleep(2)
#     mouse.position = xPos, yPos
#     print(hex(autopy.bitmap.capture_screen().get_color(xPos, yPos)))


# if __name__ == "__main__":
#     pass