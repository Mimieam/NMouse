#!/usr/bin/python

import sys
import zmq
import time
import socket

print("Server Started")
context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.setsockopt(zmq.SNDHWM, 10000)
socket.bind("tcp://*:5556")


while True:
    # socket.send_string("%i %i %i" % (11102, *mouse.position))
    string = socket.recv_multipart()
    print(string)
    res = socket.send_string("GOT IT !")
    print(res)
  # rc = zmq_connect(socket, "pgm://192.168.1.1;239.192.1.1:5555"); assert (rc == 0);