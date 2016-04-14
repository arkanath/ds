from node import Node

def startHeartbeat(self):
    print "huehuehue"

Node.startHeartbeat = classmethod(startHeartbeat)

def converge_cast_ack(self,subtreeId):
	self.ack+=1
	if self.ack==1:
		self.fragmentId = [self.self_node['id']]
	self.fragmentId.extend(subtreeId)
	if self.ack >= len(self.children):
		self.ack = 0
		if self.parent is not None:
			msg = {}
			msg['type'] = "ack_to_reiden"
			msg['msg']  = self.fragmentId
			self.send_message(self.parent['ip'],self.parent['port'],msg)
		else:
			#broadcast MOE and fragment message
			self.on_broadcast_moe(self.fragmentId)

Node.converge_cast_ack = classmethod(converge_cast_ack)

def get_moe(self):
	min_wt = sys.maxint
	min_edge = {}
	min_edge['weight'] = sys.maxint
	for neighbour in self.neighbours:
		if neighbour['id'] not in self.fragmentId:
			if min_wt > neighbour['weight']:
				min_wt = neighbour['weight']
				min_edge['inside'] = self.self_node
 				nbr = {}
 				nbr['id'] = neighbour['id']
 				nbr['ip'] = neighbour['ip']
 				nbr['port'] = neighbour['port']
 				min_edge['outside'] = nbr
 				min_edge['weight'] = min_wt
 	return min_edge

Node.get_moe = classmethod(get_moe)

def converge_cast_moe(self,edge,path):
	self.ack+=1
	if hasattr(self,'moeList'):
		self.moeList.append((edge,path))
	else:
		self.moeList = []
		self.moeList.append((edge,path))
	if self.ack >= len(self.children):
		self.ack = 0
		Path = []
		min_wt = sys.maxint
		min_edge = {}
		min_edge['weight'] = sys.maxint
		for anedge in self.moeList:
			if min_wt > anedge[0]['weight']:
				min_wt = anedge[0]['weight']
				min_edge = anedge[0]
				Path = anedge[1]
		own_moe = self.get_moe()
		if own_moe['weight'] != sys.maxint:
			if own_moe['weight'] < min_edge['weight']:
				Path = [self.self_node]
				min_edge = own_moe
			else:
				Path.append(self.self_node)
		else:
			Path.append(self.self_node)
		if self.parent is not None:
			msg = {}
			msg['type'] = 'moe_update'
			msg['edge'] = min_edge
			msg['path'] = Path
			self.send_message(self.parent['ip'],self.parent['port'],msg)
		else:
			if min_edge['weight'] != sys.maxint:
				#call root change
				pass
			else:
				pass

Node.converge_cast_moe = classmethod(converge_cast_moe)


def change_root(self, path, child):
	if 1 == len(path):
		#call the join function
		if child is not None:
			self.children.append(child)
		self.parent = None
	else:
		path = path[:-1]
		self.parent = path[-1]
		self.children.remove(path[-1])
		if child is not None:
			self.children.append(child)
		msg = {}
		msg['type'] = 'set_root'
		msg['path'] = path
		msg['child'] = self.self_node
		self.send_message(self.parent['ip'],self.parent['port'],msg)

Node.change_root = classmethod(change_root)

