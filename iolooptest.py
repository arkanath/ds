import zmq
from zmq.eventloop import ioloop, zmqstream
import signal, os, sys
import time
from  multiprocessing import Process

ioloop.install()

# loop = ioloop.IOLoop.instance()


def relay(msg):
    print "huehuehues"
    print msg

def relay2(msg):
    print "huehuehues2"
    print type(msg)

ctx = zmq.Context()

def client():
    incoming = ctx.socket(zmq.PULL)
    incoming.bind('tcp://127.0.0.1:8001')
    sincoming = zmqstream.ZMQStream(incoming)
    sincoming.on_recv(relay)
    incoming2 = ctx.socket(zmq.PULL)
    incoming2.bind('tcp://127.0.0.1:8004')
    sincoming2 = zmqstream.ZMQStream(incoming2)
    sincoming2.on_recv(relay2)
    print "started"
    ioloop.IOLoop.instance().start()
    print "stopped"

Process(target=client, args=()).start()

outgoing = ctx.socket(zmq.PUSH)
# outgoing.bind('tcp://127.0.0.1:8002')
# soutgoing = zmqstream.ZMQStream(outgoing)
outgoing.connect('tcp://127.0.0.1:8001')
outgoing.send("haha")

outgoing2 = ctx.socket(zmq.PUSH)
outgoing2.connect('tcp://127.0.0.1:8004')
sf = {}
sf['wegawegawe'] = 1241
sf['helo'] = {24:22, 45:"awgea", "wagew":67}
outgoing2.send_json(sf)
# print "huehue"