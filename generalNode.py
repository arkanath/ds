import networkx as nx
import matplotlib.pyplot as plt
from networkx import *
import signal
import json
import sys
import Queue
from collections import defaultdict
from node import *

class generalNode(Node):
    def __init__(self):
        self.startInterruptHandling()
        print "binding on", sys.argv[1]
        self.bind_receive(socket.gethostbyname(socket.gethostname()),int(sys.argv[1]))
        self.start_listening()

def main():
    G = generalNode()

if __name__ == '__main__':
    main()