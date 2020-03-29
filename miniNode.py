
import sys
import socket
import uuid
from enum import Enum
import time

import zmq

import threading
from threadingHelpers import Worker, logger
from PyQt5.QtCore import QThreadPool, pyqtSignal

signal = pyqtSignal(str)

class Status(Enum):
	ON = 1
	OFF = 0

class NodeType(Enum):
	SERVER = 0
	CLIENT = 1

TESTSERVER = 'localhost'

class ConnectedNode(object):
	""" 
	| -1,-1  |  0,-1  |  1,-1 |
	| -1, 0  |  0, 0  |  1, 0 |
	| -1, 1  |  0, 1  |  1, 1 |
	"""
	Instances = []
	def __init__(self, id=None, posID = None, posX=None, posY=None, _type=None):
		super().__init__()
		self.id = id
		self.posID = posID
		self.posX = posX
		self.posY = posY
		self.type = _type
		self.__class__.Instances += self,
	
	def printNetwork(self):
		# just to avoid recursion issues
		others = [f"<{inst.id},{inst.type.name},{inst.posID}>" for idx, inst in enumerate(self.Instances) if inst != self]
		myindex = self.Instances.index(self)
		me = f"<{self.id},{self.type.name},{self.posID}>"
		others.insert(myindex, me)
		return others 

	def __repr__(self):
		return f"""
		Id: {self.id}
		pos: ({self.posX},{self.posY})
		ntwk: {self.printNetwork()}
		""".replace('\t',' ')


class DefaultPorts(Enum):
	XREQ = 5562
	XREP = 5562
	UDP = 5563

class NetNode(object):
	_id: None
	_type: None

	def __init__(self, server_address=None, type:NodeType=None):
		super().__init__()

		self._type:Enum = type or NodeType.CLIENT
		self._id = f"{self._type.name[0]}-{str(uuid.uuid4())[:4]}"
		
		self.com_link_status:Enum = Status.OFF
		self.pub_sub_link_status: Enum = Status.OFF
		
		self.com_link = None # synchronious communication link - 
		self.pub_sub = None
		self.ip_address = None
		# addresses
		self.server = server_address
		self.clients = []

		self.isAlive = True

		# cThread = threading.current_thread() 
		# cThread.setName(f"{self._type.name}-{self._id}")
		# print(cThread)
	
	def __repr__(self):
		# print(self)
		return f"""
		Id: {self._id}
		Type: {self._type.name}
		REQ/RES Status: {self.com_link_status.name} 
		PUB/SUB Status: {self.pub_sub_link_status.name} 
		""".replace('\t','')

	def isServer(self):
		return self._type == NodeType.SERVER

	def start(self, server_addr=None, port=None):

		if (self._type == NodeType.CLIENT):
			logger.debug("Starting As Client..")
			time.sleep(5)
			self.com_link = self.connectToServer(server_addr, port)
			# logger.debug("Client is listening for server..")
			while True:
				# send a synchronization request
				self.send(f'~Client~{self._id} Connected! XREQ')
				logger.debug('Client awaiting response <==')

				# # wait for synchronization reply
				# msg = self.com_link.recv_multipart()
				# logger.debug(f' received ->{msg}')
				self.listen()
		else:
			logger.debug("Starting As Server..")
			
			self.com_link = self.startService()
			ConnectedNode(id=self._id, _type=NodeType.SERVER)  # add the server to the network list in connectedNode instance
			self.listen()



	# Client functions
	def getServerInfo(self):
		if (self._type == NodeType.SERVER):
			return self.ip_address
		return self.server

	def setServer(self, server):
		self.server = server
	
	def connectToServer(self, server_addr, port):
		server_addr = server_addr or self.server
		port = port or DefaultPorts.XREQ.value
		
		context = zmq.Context()
		syncclient = context.socket(zmq.XREQ)
		syncclient.setsockopt(zmq.IDENTITY, f'{self._id}'.encode('utf-8'))

		try:
			syncclient.connect(f'tcp://{server_addr}:{port}')
		except zmq.error.ZMQError as err:
			logger.error(f"Failed to Connect to Server {server_addr}:{port}")
			self.com_link_status = Status.OFF
		else:
			logger.info(f"{self._id} is connected to Server {server_addr}:{port}")
			self.com_link_status = Status.ON

		return syncclient
 
	# server functions
	def becomeServer(self):
		raise NotImplementedError

	def startService(self, port=None):
		"""
			the service that connectToServer will contact
		"""

		port = port or DefaultPorts.XREQ.value

		context = zmq.Context()
		syncservice = context.socket(zmq.XREP)
		try:
			syncservice.bind(f"tcp://*:{port}")
		except zmq.error.ZMQError as err:
			logger.error(f"{self._id} Failed to start service on {port}, {err}")
			self.com_link_status = Status.OFF
		else:
			logger.info(f"{self._id} Server Service Started on port {port}")
			self.com_link_status = Status.ON

		return syncservice


	def killNode(self):
		raise NotImplementedError
	
	def send(self, msg):
		# self.com_link.send(b'Client ==> Hello')
		# msg = self.com_link.recv()
		# msg = self.com_link.recv_multipart()
		self.com_link.send(f"{msg}".encode('utf-8'))
		logger.debug(f"[{self._id}] Sending=> {msg}")

	def listen(self):

		while self.isAlive:
			logger.debug(f"{self._type.name} listening>>")
			self.send("start/Hello World from server")
			client_id, msg = self.com_link.recv_multipart()
			logger.debug([client_id, msg])
			# logger.info(msg)
			if self.isServer():
				self.clients.append(ConnectedNode(id=client_id, _type=NodeType.CLIENT))
				# time.sleep(2)

if __name__ == "__main__":
	SN = NetNode(type=NodeType.SERVER)
	CN = NetNode()
	CN2 = NetNode()

	# CN.setServer(TESTSERVER)
	# CN2.setServer(TESTSERVER)

	workers = [
		(Worker(SN.start), 0),
		# (Worker(CN.start), 2),
		# (Worker(CN2.start), 0),
		(Worker(NetNode(server_address=TESTSERVER).start), 2),
		(Worker(NetNode(server_address=TESTSERVER).start), 0),
		(Worker(NetNode(server_address=TESTSERVER).start), 0),
		(Worker(NetNode(server_address=TESTSERVER).start), 0),
	]
	threadpool = QThreadPool()

	def startWithDelay(worker, delay):
		time.sleep(delay)
		threadpool.start(worker)

	[startWithDelay(w, d) for w, d in workers]
	
	# server1 = (Worker(SN.start, 0))
	# client1 = Worker(CN.start)
	# threadpool.start(server1)
	# threadpool.start(client1)	
	# time.sleep(10)
	# CN.listen()

	print(SN)
	print(CN)

	while True:
		# SN.send("Hello World")
		time.sleep(2)
		# print(SN.clients)

	print("Exiting :)")