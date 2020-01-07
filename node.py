#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import threading
import time
import zmq
import uuid
import socket
import logging
import sys
import logging

from threadingHelpers import logger
# from threadingHelpers import logger

# UDP
UDP_PORT = 5563
# XREQ/REP
XREQ_XREP_PORT = 5562
# PUB/SUB
PUB_SUB_PORT = 5556

# extra = {'type':'Super App'}


# logger = logging.LoggerAdapter(logger, extra)


_id = f"Node-{str(uuid.uuid4())[:4]}"


def upd_server_discovery(addr='255.255.255.255', port=5563, every=3):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(False)
    start_time = time.time()
    message =  bytes(f"SERVER ON - {_id}", 'utf-8')
    while True:
        elapsed_time = time.time() - start_time
        logger.debug(f"message = {message}, {(addr, port)}")
        server.sendto(message, (addr, port))
        elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        logger.debug(f"UDP: broadcast {addr, port} - message <<{message}>> sent! {elapsed_time_str}")
        try:
            data, incoming_addr = server.recvfrom(1024)
            logger.info("received message: %s from [%s]"%(data, incoming_addr))
        except BlockingIOError as e:
            pass
        time.sleep(every)

def udp_client_discovery(port=5563, timeout=30, every=3):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set some options to make it multicast-friendly
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
            pass # Some systems don't support SO_REUSEPORT
    client.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
    client.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)


    client.bind(('', port))
    client.setblocking(False)
    # client.settimeout(3)

    start_time = time.time()
    found = []
    while True:
        elapsed_time = time.time() - start_time
        try:
            data, addr = client.recvfrom(1024)
            logger.info("received message: %s from [%s]"%(data, addr))
            if addr:
                found.append(addr)
        except BlockingIOError as e:
            logger.info(f"{_id} >> looking for Server ... [UDP]")
        finally:
            elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            logger.info(f"{_id} -- elapsed time = {elapsed_time_str}")
            if timeout and elapsed_time > timeout:
                logger.warning(f"{_id} >> timeout")
                return found
        time.sleep(every)
                
        

def start_as_server():
    def _broadcast_identity(_q=None, every=3):
        logger.info(f"[{threading.current_thread().getName()}]-{_id} >> Broadcasting...: I'm The Server ")
        upd_server_discovery(every=every)
             

    logger.info(f"{_id} -- Initializing new Server")
    logger.info(f"{_id} -- Setting up PUBLISHER on New Thread")

    pub_thread = threading.Thread(target=_broadcast_identity)
    # pub_thread.daemon=True
    logger.info(f"[{threading.current_thread().getName()}]{_id} -- continiously broadcast That I'm the server unless i receive a TAKEOVER msg")
    pub_thread.start()
    # Prepare our context and sockets
    context = zmq.Context()

    syncservice = context.socket(zmq.XREP)
    syncservice.bind('tcp://*:5562')
    logger.info("start_as_server")
    
    every = 3
    while True:
        logger.info(f"[{threading.current_thread().getName()}]-{_id} >> Broadcasting...: I'm The Server ")
        time.sleep(every)
        logger.info('waiting got something? ->')
            # wait for synchronization request
        msg = syncservice.recv_multipart()
        logger.info(msg)
        # send synchronization reply
        syncservice.send_multipart([msg[0], b'Server Publisher Ready!'])
        syncservice.send_multipart([msg[0], b'sending this again!'])

def start_as_client(server_addr="localhost"):
    context = zmq.Context()
    syncclient = context.socket(zmq.XREQ)
    syncclient.connect(f'tcp://{server_addr}:5562')
    logger.info("start_as_client")
    while True:
        logger.info('sending XREQ ->')
        # send a synchronization request
        syncclient.send(b'HELLO XREQ ')
        logger.info('Waiting... for resp?')

        # wait for synchronization reply
        msg = syncclient.recv_multipart()
        logger.info(msg)

def setup_pub_sub_socket(isServer, server_addr='', server_port=''):
    context = zmq.Context()
    socket = None

    if isServer:
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:{server_port}")
    else:
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://{server_addr}:{server_port}")
        logger.info("PUB/SUB set up")
        socket.setsockopt_string(zmq.SUBSCRIBE, "")

# # tcp broadcast that i'm here
# def broadcast(msg='', timeout=None):
#     start_time = time.time()
#     anyRes = []
#     while not anyRes:
#         logger.info(f"{_id} >> broadcasting and sleeping for 5 sec")
#         upd_server_discovery()
#         logger.info(f"{_id} << received anything ? {anyRes}")
#         elapsed_time = time.time() - start_time
#         elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
#         logger.info(f"{_id} -- elapsed time = {elapsed_time_str}")
#         if timeout and elapsed_time > timeout:
#             logger.info(f"{_id} >> Done Broadcasting - no server found")
#             return anyRes
#         time.sleep(5)
#     return anyRes


def start(progress_callback):
    logger.info(f"{_id} Started")
    
    progress_callback.emit(0*100/4)
    disc_timeout = int(sys.argv) if  len(sys.argv) > 1 and sys.argv[1] else 3
    found = udp_client_discovery(timeout=disc_timeout)
    progress_callback.emit(2*100/4)
    if found:
        logger.warning(f"{_id} >> a server was found - Setting up pub/sub to {found}")
        [(server_addr, port)] = found
        progress_callback.emit(4*100/4)
        start_as_client(server_addr)
    else:
        progress_callback.emit(4*100/4)
        logger.warning(f"{_id} -- No Server Found -- Initializing new Server")
        start_as_server()
        # initialize_new_server()

if __name__ == "__main__":
    # from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    # app = QApplication([])
    # window = QWidget()
    # layout = QVBoxLayout()
    # layout.addWidget(QPushButton('Top'))
    # layout.addWidget(QPushButton('Bottom'))
    # window.setLayout(layout)
    # window.show()
    # app.exec_()
    
    # print(app)
    # print(window)


    logger.info(f"{_id} Started")
    
    disc_timeout = int(sys.argv) if  len(sys.argv) > 1 and sys.argv[1] else 3
    found = udp_client_discovery(timeout=disc_timeout)

    if found:
        logger.warning(f"{_id} >> a server was found - Setting up pub/sub to {found}")
        [(server_addr, port)] = found
        start_as_client(server_addr)
    else:
        logger.warning(f"{_id} -- No Server Found -- Initializing new Server")
        start_as_server()
        # initialize_new_server()
        






