import networkx as nx
from transporter_api import Transporter
import matplotlib.pyplot as plt
from networkx import *
import signal
import json
import sys
import Queue
from collections import defaultdict


class MasterNode(Transporter):
    def on_receive(self, msg):
        print "Received:", msg
        for m in msg:
            decoded_json = json.loads(m)
            type = decoded_json['type']
            if type == 'send_along_path':
                self.handleAlongPath(decoded_json)

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
            for line in f:
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
                    replication_preferences.append((int(x[0]), int(x[1])))
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
        for edge in preferredEdgeSet:
            G[edge[0]][edge[1]]['weight'] = -sys.maxint
        return G

    def unprefMSTedges(self, prefEdgeSet, G):
        for edge in preferredEdgeSet:
            G[edge[0]][edge[1]]['weight'] = sys.maxint
        return G

    def MSTConstruction(self, G):
        T = nx.minimum_spanning_tree(G)
        return T

    def getParentChildrenPathFromMST(self):
        print "hueh"

    def handleAlongPath(self, msg):
        if len(msg['remaining_path']) > 0:
            ip, port = msg['remaining_path'][0]
            msg['remaining_path'].remove(msg['remaining_path'][0])
            self.send_message(ip, port, msg)
        else:
            print "reached at node", msg['msg']

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

    def sendMSTInfos(self, signal, frame):
        parent, children, path = self.getTreePaths(self.mst, '1')
        print "caught"
        for node in self.G.nodes():
            print node
            info = {}
            info['self_node'] = self.node_infos[node]
            info['parent'] = self.node_infos[parent[node]]
            info['children'] = [self.node_infos[l] for l in children[node]]
            msg = {}
            msg['type'] = 'send_along_path'
            msg['remaining_path'] = []
            for l in path[node]:
                msg['remaining_path'].append((self.node_infos[l]['ip'],self.node_infos[l]['port']))
            msg['msg'] = info
            print self.node_infos[node]['ip'],self.node_infos[node]['port']
            self.send_message(self.node_infos[node]['ip'],self.node_infos[node]['port'],msg)
            print "done"
            # break

    def bhagbc(self, signal, frame):
        print "       huehuehue bye"
        sys.exit(0)

    def __init__(self, name):
        signal.signal(signal.SIGINT, self.sendMSTInfos)
        signal.signal(signal.SIGTSTP, self.bhagbc)
        nodes, edges, rep = self.readFile(name)
        self.node_infos = {}
        for node in nodes:
            self.node_infos[node['id']] = node
        self.node_infos[None] = None
        self.G = self.getGraph(nodes, edges)
        self.rep_pref = rep
        self.mst = self.MSTConstruction(self.G)
        # nx.draw(self.mst)
        # plt.draw()
        # plt.show()
        self.bind_receive('127.0.0.1',8005)
        self.start_listening()


def main():
    M = MasterNode('input.txt')


if __name__ == '__main__':
    main()
