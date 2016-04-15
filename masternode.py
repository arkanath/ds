import networkx as nx
import matplotlib.pyplot as plt
from networkx import *
import signal
import json
import sys
import Queue
from collections import defaultdict
from node import *
import pylab
import threading
import thread
from multiprocessing import Process


class MasterNode(Node):
    def add_neighbor_info(self,msg):
        neighbors_info ={'parent':msg['parent'],
                        'children': msg['children'],
                        }
        self.neighbors_info_dic[msg['id']]=neighbors_info
        if len(self.neighbors_info_dic) == len(self.fragmentId):
            # print "sentprint", self.neighbors_info_dic
            self.printNewMST(self.neighbors_info_dic)
            self.neighbors_info_dic = {}

    def getGraph(self, nodes, edges):
        G = nx.Graph()
        list_of_nodes = []
        for node in nodes:
            list_of_nodes.append(node['id'])
        G.add_nodes_from(list_of_nodes)

        list_of_edges = []
        for edge in edges:
            weight = dict()
            weight['weight'] = edge[2]
            list_of_edges.append((edge[0], edge[1], weight))
        G.add_edges_from(list_of_edges)
        return G

    def readFile(self, filename):
        machine = -1
        nodes = []
        numedges = -1
        edges = []
        numreplications = -1
        replication_preferences = []
        with open(filename, 'r') as f:
            lines = f.readlines()
        self.root_id = lines[0].strip()
        lines = lines[1:]
        for line in lines:
            line = line[:-1]
            if machine == -1:
                machine = int(line)
            elif machine > 0:
                machine -= 1
                x = line.split(':')
                node_info = {}
                node_info['id'] = x[0]
                node_info['ip'] = x[1]
                node_info['port'] = int(x[2])
                nodes.append(node_info)
            elif numedges == -1:
                numedges = int(line)
            elif numedges > 0:
                numedges -= 1
                x = line.split()
                x[2] = int(x[2])
                edges.append(x)
            elif numreplications == -1:
                numreplications = int(line)
            elif numreplications > 0:
                numreplications -= 1
                x = line.split()
                replication_preferences.append((x[0], x[1]))
            else:
                continue
        return nodes, edges, replication_preferences

    def reduceEdgeWeights(self, G, repNodes):
        k = 1;  # Need to be set to some weight for weight reduction
        for pair in repNodes:
            if nx.has_path(G, source=pair[0], target=pair[1]):
                paths = nx.all_simple_paths(G, source=pair[0], target=pair[1])
                for path in paths:
                    pathLength = len(path) - 1
                    # print "pair", pair
                    # print "path:",path
                    # print "length:",pathLength
                    for i in range(0, pathLength):
                        # print "here"
                        # print path[i], path[i+1]
                        # print "weight", G[path[i]][path[i + 1]]['weight']
                        G[path[i]][path[i + 1]]['weight'] = G[path[i]][path[i + 1]]['weight'] - float(k / pathLength)
        return G

    # to set the edge weight of user specified edges in the MST to negative infinity
    # so that those edges are always included in the MST constructed.
    def prefMSTedges(self, prefEdgeSet, G):
        Gret = nx.Graph(G)
        for edge in prefEdgeSet:
            Gret[edge[0]][edge[1]]['weight'] = -100000
        return Gret

    def unprefMSTedges(self, prefEdgeSet, G):
        for edge in prefEdgeSet:
            G[edge[0]][edge[1]]['weight'] = sys.maxint
        return G

    def MSTConstruction(self, G):
        T = nx.minimum_spanning_tree(G)
        return T

    def getTreePaths(self, T, rootID):
        flag = True
        path = defaultdict(list)
        que = Queue.Queue()
        que.put(rootID)
        parent = {rootID: None}
        path[rootID] = []
        children = defaultdict(list)
        visited = []

        while not que.empty():
            current = que.get()
            visited.append(current)
            neighbors = T.neighbors(current)
            children[current] = []
            for neighbor in neighbors:
                if neighbor not in visited:
                    que.put(neighbor)
                    parent[neighbor] = current
                    children[current].append(neighbor)
                    path[neighbor] = list(path[current])
                    path[neighbor].append(neighbor)
        return parent, children, path

    def sendMSTInfos(self):
        parent, children, path = self.getTreePaths(self.mst, '1')
        # print "caught"
        for node in self.G.nodes():
            # print node
            info = {}
            info['master_node'] = self.node_infos[self.root_id]
            info['self_node'] = self.node_infos[node]
            info['parent'] = self.node_infos[parent[node]]
            info['children'] = [self.node_infos[l] for l in children[node]]
            nbrs = self.G.edges(node, True)
            neighbors_list = []
            for x in nbrs:
                nb = {}
                nb['id'] = x[1]
                nb['ip'] = self.node_infos[nb['id']]['ip']
                nb['port'] = self.node_infos[nb['id']]['port']
                nb['weight'] = x[2]['weight']
                neighbors_list.append(nb)
            info['neighbors'] = neighbors_list
            msg = {}
            msg['type'] = 'send_init_along_path'
            msg['remaining_path'] = []
            for l in path[node]:
                msg['remaining_path'].append((self.node_infos[l]['ip'], self.node_infos[l]['port']))
            msg['msg'] = info
            # print self.node_infos[node]['ip'], self.node_infos[node]['port']
            self.send_message(self.node_infos[node]['ip'], self.node_infos[node]['port'], msg)
            # print "done"
            # break

    def printNewMST(self, treeInfo):
        self.rootedTree = nx.DiGraph()
        for key, value in treeInfo.iteritems():
            if value['parent'] != None:
                self.rootedTree.add_edge(key, value['parent']['id'], weight=self.G[key][value['parent']['id']]['weight'])
            for ch in value['children']:
                self.rootedTree.add_edge(ch['id'], key, weight=self.G[ch['id']][key]['weight'])
        threading.Thread(target=self.printMST(self.rootedTree)).start()

    def printMST(self, rooted_tree):
        pylab.close()
        pos = nx.spring_layout(rooted_tree)
        node_labels = {node: node for node in rooted_tree.nodes()}
        edge_labels = dict([((u, v,), d['weight'])
                            for u, v, d in rooted_tree.edges(data=True)])
        nx.draw_networkx_labels(rooted_tree, pos, labels=node_labels)
        nx.draw_networkx_edge_labels(rooted_tree, pos, edge_labels=edge_labels)
        nx.draw(rooted_tree, pos, arrows=True)
        pylab.savefig('plot.pdf')

    def __init__(self, name):
        self.neighbors_info_dic = {}
        self.startInterruptHandling()
        nodes, edges, rep = self.readFile(name)
        self.node_infos = {}
        for node in nodes:
            self.node_infos[node['id']] = node
        self.node_infos[None] = None
        self.G = self.getGraph(nodes, edges)
        self.rep_pref = rep
        self.G_updated = self.prefMSTedges(rep, self.G)  # change weights of preferred MST edges
        self.mst = self.MSTConstruction(self.G_updated)
        parent, children, path = self.getTreePaths(self.mst, '1')
        self.rootedTree = nx.DiGraph()
        self.partialTree = []
        for x in self.G.nodes():
            if parent[x] != None:
                self.rootedTree.add_edge(x, parent[x], weight=self.G[x][parent[x]]['weight'])
            for ch in children[x]:
                self.rootedTree.add_edge(ch, x, weight=self.G[ch][x]['weight'])
        self.printMST(self.rootedTree)
        # print "binding on",socket.gethostbyname(socket.gethostname()), sys.argv[1]
        self.bind_receive("*", int(sys.argv[1]))
        self.start_listening()


def main():
    # pass
    M = MasterNode('input.txt')


if __name__ == '__main__':
    main()
