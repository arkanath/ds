import networkx as nx
import Queue

def getTreeInfo(self, T, rootID):
	flag = True
	path = {}
	que = Queue.Queue()
	que.put(rootID)
	parent = {rootID:-1}
	path = {rootID:rootID}
	children = {}
	visited = []

	while !que.empty():
		current = que.get()
		visited.append(current)
		neighbors = T.neighbors(current)
		child = []
		for neighbor in neighbors:
			if neighbor not in visited:
				que.put(neighbor)
				parent[neighbor] = current
				child.append(neighbor)
				l = path[current]
				l.append(neighbor)
				path[neighbor] = l
		children[parent] = child


	return parent, children, path


