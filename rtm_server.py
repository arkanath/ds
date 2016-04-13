import socket
from twisted_api import *


class Echo(protocol.Protocol):
    """This is just about the simplest possible protocol"""
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print self.transport.getPeer()
        self.transport.write(data)
        print type(data)



def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    print socket.gethostbyname(socket.gethostname())
    reactor.listenTCP(8000,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
