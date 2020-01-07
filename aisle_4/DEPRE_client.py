#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import zmq
import time
import socket


import autopy
from pynput.mouse import Button, Controller

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

mouse = Controller()


print("Collecting updates from weather server…")
socket.connect("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "11102"

# Python 2 - ascii bytes to unicode str
if isinstance(zip_filter, bytes):
    zip_filter = zip_filter.decode('ascii')
# subscribe to messaged PREFIXED with zipfilter
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# Process 5 updates
total_temp = 0

while True:
    string = socket.recv_string()
    print(string)
    # socket.send_string("Yo Buddy")
    # uid, xPos, yPos = string.split()
    # xPos = int(xPos)
    # yPos = int(yPos)
    # # time.sleep(2)
    # mouse.position = xPos, yPos
    # print(hex(autopy.bitmap.capture_screen().get_color(xPos, yPos)))
    
    
    # mouse.move(xPos, yPos)
    # autopy.mouse.smooth_move(xPos, yPos)
# print("Average temperature for zipcode '%s' was %dF" % (
#       zip_filter, total_temp / (update_nbr+1))
# )


#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

# import zmq

# context = zmq.Context()

# #  Socket to talk to server
# print("Connecting to hello world server…")
# socket = context.socket(zmq.REQ)
# socket.connect("tcp://localhost:5555")

# #  Do 10 requests, waiting each time for a response
# for request in range(10):
#     print("Sending request %s …" % request)
#     socket.send(b"Hello")

#     #  Get the reply.
#     message = socket.recv()
#     print("Received reply %s [ %s ]" % (request, message))

import ipaddress
import netifaces
import pandas as pd

# determine my current network - name, address, subnet
gws = netifaces.gateways()  
addr, interface_name = gws['default'][netifaces.AF_INET] 
network_info = netifaces.ifaddresses(interface_name)[netifaces.AF_INET]  
address, netmask, broadcast = network_info[0].values() 

n = ipaddress.ip_interface(f'{address}/{netmask}').network   
# list(n)[1:-1]  
ip_list = [ str(x) for x  in n][1:-1]   

df = pd.DataFrame(ip_list, columns=['ip'])
df['port'] = 80
df['is_up'] = False

df[is_up].apply(is_up)

def is_up(addr, port): 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
        return s.connect_ex((addr, port)) == 0 

import socket
def is_up(addr, port):
    status = False
    socket.create_connection((addr, port), timeout=1)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    try:
        # doesn't even have to be reachable
        s.connect((addr, port))
        print(s.getsockname())
        status = True
    except:
        pass
    finally:
        s.close()
    return status