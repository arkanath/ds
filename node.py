import networkx as nx
class Node:
	def __init__(self):
		# self.G = getGraph()
		# self.name = str
		self.fragmentId = set()
		self.state = "reiden/broadcastecho"
		self.rootid =
		self.id =
		self.parent =
		self.children =
		self.ack = 0

	def startHeartbeat():

	def stopHeartbeat():

	def setHeartbeatInterval():

	def listenToHeartbeat():

	def sendmsgtoroot():
		if self.id == self.rootid:
			self.state = "broadcastecho"
			broadcastToChildren("reiden")
			return
		# send message to parent

	def broadcastToChildren(message):
		# for changing the state to reiden once the root has already known that that there is an edge failure
		state = "reiden"
		#sends reiden to all its children 		

	def covergeCast():
		self.ack += 1
		if self.ack < len(self.children):
			

	def changeRoot():

