import networkx as nx
class Node:
	def __init__(self):
		# self.G = getGraph()
		# self.name = str
		self.state = "reiden/broadcastecho"
		self.root = "0"
		self.self_node = "0"
		self.fragmentId = "0"
		self.parent = "0"
		self.children = ["0"]
		self.ack = 0

	def startHeartbeat():
		pass

	def stopHeartbeat():
		pass

	def setHeartbeatInterval():
		pass

	def listenToHeartbeat():
		pass

	def sendmsgtoroot():
		if self.id == self.rootid:
			self.state = "broadcastecho"
			broadcastToChildren("reiden")
			return
		# send message to parent

	def broadcastToChildren(message):
		#for changing the state to reiden/find once the root has already known that that there is an edge failure
		state = message
		#set fragmentid to set of all nodes when message is findmoe
		#sends reiden/find to all its children 		

	def convergeCast(subtree):
		self.ack += 1
		self.fragmentId = self.fragmentId.union(subtree)
		if self.ack == len(self.children):
			#send acknowledgement and fragmentId to parent
			if self.root["id"] == self.self_node["id"]:
				broadcastToChildren("findMOE")
			return

	def convergeCastMOE(path,edge,weight):


	def changeRoot():

