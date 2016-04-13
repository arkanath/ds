import networkx as nx

class MasterNode:
	def getGraph(self,nodes,edges):
		G = nx.Graph()
		list_of_nodes = []
		for i in range(1,nodes+1):
			list_of_nodes.append(i)
		G.add_nodes_from(list_of_nodes)
		list_of_edges = []
		for edge in edges:
			weight = dict()
			weight['weight'] = edge[2]
			list_of_edges.append((edge[0],edge[1],weight))
		G.add_edges_from(list_of_edges)
		return G

	def readFile(self,name):
		machine = -1
		ip = []
		port = []
		numedges = -1
		edges = []
		numreplications = -1
		reps = []
		with open(name,'r') as f:
			for line in f:
				line = line[:-1]
				if machine==-1:
					machine = int(line)
				elif machine>0:
					machine-=1
					x = line.split(':')
					ip.append(x[0])
					port.append(x[1])
				elif numedges==-1:
					numedges = int(line)
				elif numedges>0:
					numedges-=1
					x = line.split()
					edge=[]
					edge.append(int(x[0]))
					edge.append(int(x[1]))
					edge.append(int(x[2]))
					edges.append(edge)
				elif numreplications==-1:
					numreplications = int(line)
				elif numreplications>0 :
					numreplications -=1
					x = line.split()
					reps.append((int(x[0]),int(x[1])))
				else:
					continue
		return ip,port,edges,reps

	def reduceEdgeWeight(self, G, repNodes):
		k = 1; #Need to be set to some weight for weight reduction
		for pair in repNodes:
			if nx.has_path(G,source = pair[0], target = pair[1]):
				path = nx.shortest_path(G, source = pair[0], target = pair[1])
				pathLength = len(path) - 1
				# print "pair", pair
				# print "path:",path
				# print "length:",pathLength
				for i in range(0, pathLength):
					# print "here"
					# print path[i], path[i+1]
					# print "weight", G[path[i]][path[i + 1]]['weight']
					G[path[i]][path[i + 1]]['weight'] = G[path[i]][path[i + 1]]['weight'] - float(k/pathLength)
		return G

	#to set the edge weight of user specified edges in the MST to negative infinity
	#so that those edges are always included in the MST constructed.
	def prefMSTedges(self, prefEdgeSet, G):
		for edge in preferredEdgeSet:
			G[edge[0]][edge[1]]['weight'] = -sys.maxint
		return G

	def unprefMSTedges(self, prefEdgeSet, G):
		for edge in preferredEdgeSet:
			G[edge[0]][edge[1]]['weight'] = sys.maxint
		return G

	def MSTConstructio(self, G):
		T = nx.minimum_spanning_tree(G)
		return T


	def __init__(self,name):
		ip,port,edges,rep = self.readFile(name)
		nodes = len(ip)
		self.G = self.getGraph(nodes,edges)
		self.ip =ip
		self.port = port
		self.rep = rep
		all_paths = nx.all_simple_paths(self.G, source=1, target=3)
		for path in all_paths:
			print(path)

		G1 = self.reduceEdgeWeight(self.G, rep)
		# for edge in nx.edges(G1):
		# 	print G1[edge[0]][edge[1]]['weight']

def main():
	M = MasterNode('input.txt')

if __name__ == '__main__':
	main()