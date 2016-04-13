import socket
from twisted_api import *
from threading import Thread
import time
import signal, os, sys

class RTMClient(TwistedClient):
    active_connections = {}
    id_to_key = {}
    th = 0
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print "Server at", self.transport.getPeer,"said:", data
        # self.transport.loseConnection()

    def connectionMade(self):
        self.transport.write("this is the end")
        RTMClient.active_connections[self.transport.getPeer()]=self

    def connectionLost(self, reason):
        print "Losing Connection",reason
        RTMClient.active_connections.pop(self.transport.getPeer(), None)

    def closeConnection(self, key):
        RTMClient.active_connections[key].loseConnection()

    def closeConnection(self, id):
        RTMClient.active_connections[RTMClient.id_to_key[id]].loseConnection()

    def makeNewConnection(self, ip, port, id="default"):
        self.f = TwistedFactory()
        self.f.setProtocolClass(RTMClient)
        reactor.connectTCP(ip, port, self.f)
        reactor.run()
        if id=="default":
            RTMClient.id_to_key[ip+":"+str(port)] = address.IPv4Address('TCP', ip, port)
        else:
            RTMClient.id_to_key[id] = address.IPv4Address('TCP', ip, port)

    def send_message(self, id, msg):
        if id not in RTMClient.id_to_key or RTMClient.id_to_key[id] not in RTMClient.active_connections:
            print "connection not established for id:", id
            return
        print RTMClient.active_connections
        print RTMClient.id_to_key
        RTMClient.active_connections[RTMClient.id_to_key[id]].transport.write(msg)
        RTMClient.active_connections[RTMClient.id_to_key[id]].transport.doWrite()

    def stop(self):
        if reactor.running:
            reactor.stop()
            if reactor.running:
                print "What.."
            else:
                print "Reactor stopped"
        else:
            print "Reactor already stopped"

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C - or killed me with -2'
signal.signal(signal.SIGINT, signal_handler)
h = RTMClient()
h.makeNewConnection('127.0.0.1', 8001, "w")
# h.makeNewConnection('127.0.0.1', 8010, "w2")
# time.sleep(1)
# h.send_message("w2","huehuehue2")