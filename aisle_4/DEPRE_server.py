
import zmq
import sys
import threading
import time
from random import randint, random

__author__ = "Felipe Cruz <felipecruz@loogica.net>"
__license__ = "MIT/X11"

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'worker-%d' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect('tcp://localhost:5570')
        print('Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        reqs = 0
        while True:
            reqs = reqs + 1
            print('Req #%d sent..' % (reqs))
            socket.send_string(u'request #%d' % (reqs))
            for i in range(5):
                sockets = dict(poll.poll(1000))
                if socket in sockets:
                    msg = socket.recv()
                    tprint('Client %s received: %s' % (identity, msg))

        socket.close()
        context.term()

class ServerTask(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:5570')

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        workers = []
        for i in range(5):
            worker = ServerWorker(context)
            worker.start()
            workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()

class ServerWorker(threading.Thread):
    """ServerWorker"""
    def __init__(self, context):
        threading.Thread.__init__ (self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        tprint('Worker started')
        while True:
            ident, msg = worker.recv_multipart()
            tprint('Worker received %s from %s' % (msg, ident))
            replies = randint(0,4)
            for i in range(replies):
                time.sleep(1. / (randint(1,10)))
                worker.send_multipart([ident, msg])

        worker.close()


def main():
    """main function"""
    server = ServerTask()
    server.start()
    for i in range(3):
        client = ClientTask(i)
        client.start()

    server.join()


if __name__ == "__main__":
    main()


# import zmq
# import time
# from random import randrange
# from pynput.mouse import Button, Controller

# mouse = Controller()

# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.bind("tcp://*:5556")


# while True:
#     # zipcode = randrange(1, 100000)
#     # temperature = randrange(-80, 135)
#     # relhumidity = randrange(10, 60)
#     print("%i %i %i" % (11102, *mouse.position))
#     # socket.send_string("%i %i %i" % (zipcode, temperature, relhumidity))
#     socket.send_string("%i %i %i" % (11102, *mouse.position))
    
#     time.sleep(0.5)
# #
# #   Hello World server in Python
# #   Binds REP socket to tcp://*:5555
# #   Expects b"Hello" from client, replies with b"World"
# #

# # import time
# # import zmq

# # context = zmq.Context()
# # socket = context.socket(zmq.PUB)
# # socket.bind("tcp://*:5556")

# # while True:
# #     #  Wait for next request from client
# #     message = socket.recv()
# #     print("Received request: %s" % message)

# #     #  Do some 'work'
# #     time.sleep(1)

# #     #  Send reply back to client
# #     socket.send(b"World")

