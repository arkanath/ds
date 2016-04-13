from node import Node

def startHeartbeat(self):
    print "huehuehue"

Node.startHeartbeat = classmethod(startHeartbeat)

