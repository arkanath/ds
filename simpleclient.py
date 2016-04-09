
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example client. Run simpleserv.py first before running this.
"""

from twisted.internet import reactor, protocol


# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    
    def connectionMade(self):
        self.transport.write("hello, world!")
    
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print "Server said:", data
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print "connection lost"


class cli(EchoClient):
    def __init__(self):
        self.message_to_be_sent = "l"

    def connectionMade(self):
        self.transport.write(self.message_to_be_sent)

    def run(self):
        self.message_to_be_sent = "huehuehue"
        self.f = EchoFactory()
        reactor.connectTCP("localhost", 8000, self.f)
        reactor.run()


class EchoFactory(protocol.ClientFactory):

    protocol = cli

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()

# this connects the protocol to a server running on port 8000
# def main():
#     f = EchoFactory()
#     reactor.connectTCP("localhost", 8010, f)
#     reactor.run()
#
# # this only runs if the module was *not* imported
# if __name__ == '__main__':
#     main()

hola = cli()
hola.run()