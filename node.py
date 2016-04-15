from transporter_api import Transporter
import networkx as nx
import socket
import json
from pprint import pprint
import time
import signal
import sys
from threading import Timer
from collections import defaultdict
import logging
logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.WARNING)

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class Node(Transporter):
    def on_receive(self, msg):
        logger.debug("Received: "+ str(msg))
        for m in msg:
            decoded_json = json.loads(m)
            type = decoded_json['type']
            if type == 'send_init_along_path':
                self.handleInitAlongPath(decoded_json)
            elif type == 'heartbeat':
                self.handleHeartbeat(decoded_json)
            elif type == 'heartbeat_ack':
                self.handleHeartbeatAck(decoded_json)
            elif type == 'send_msg_to_root':
                self.send_msg_to_root(decoded_json)
            elif type == 'broadcast_reiden':
                self.broadcast_reiden(decoded_json)
            elif type == 'broadcast_moe':
                self.broadcast_moe(decoded_json)
            elif type == 'ack_to_reiden':
                self.converge_cast_ack(decoded_json['msg'])
            elif type == 'moe_update':
                self.converge_cast_moe(decoded_json['edge'], decoded_json['path'])
            elif type == 'neighbors_info':
                self.add_neighbor_info(decoded_json)
            elif type == 'set_root':
                self.change_root(decoded_json['path'], decoded_json['child'], decoded_json['edge'])
            elif type == 'join_request':
                self.handle_join(decoded_json)
            elif type == 'formation_completed':
                self.broadcast_completion_info(decoded_json)
            elif type == 'neighbors_info':
                self.add_neighbor_info(decoded_json)

    def handleInitAlongPath(self, msg):
        if len(msg['remaining_path']) > 0:
            ip, port = msg['remaining_path'][0]
            msg['remaining_path'].remove(msg['remaining_path'][0])
            self.send_message(ip, port, msg)
        else:
            self.self_node = msg['msg']['self_node']
            self.master_node = msg['msg']['master_node']
            self.fragmentId = [msg['msg']['self_node']['id']]
            self.parent = msg['msg']['parent']
            self.children = msg['msg']['children']
            self.neighbors = msg['msg']['neighbors']
            self.join_request = []
            self.root_changed = False
            for l in self.neighbors:
                l['timestamp'] = int(round(time.time() * 1000))
            self.ack = 0
            pprint(vars(self))
            self.startHeartbeat()

    def startHeartbeat(self):
        RepeatedTimer(1, self.callbackHeartbeat)

    def handleHeartbeat(self, msg):
        if not hasattr(self,'neighbors'):
            print "early heartbeat"
            return
        for l in self.neighbors:
            if l['id'] == msg['from']:
                l['timestamp'] = int(round(time.time() * 1000))
                msg = {'type': 'heartbeat_ack', 'from': self.self_node['id']}
                self.send_message(l['ip'], l['port'], msg)

    def handleHeartbeatAck(self, msg):
        for l in self.neighbors:
            if l['id'] == msg['from']:
                l['timestamp'] = int(round(time.time() * 1000))

    def callbackHeartbeat(self):
        logger.debug("heartbeatcheck!")
        newneighbors = []
        toberemoved = []
        for l in self.neighbors:
            curr_time = int(round(time.time() * 1000))
            if l['timestamp'] < curr_time - 2000:
                logger.debug("timeout, removing"+str(l))
                toberemoved.append(l)
                continue
            else:
                newneighbors.append(l)
                if l['id'] > self.self_node['id']:
                    msg = {'type': 'heartbeat', 'from': self.self_node['id']}
                    self.send_message(l['ip'], l['port'], msg)

        self.neighbors = newneighbors
        for x in toberemoved:
            self.on_link_failure(x['id'])

    def removeFromNeighbors(self, idlist):
        newneighbors = []
        toberemoved = []
        for x in self.neighbors:
            if x['id'] in idlist:
                logger.debug("removing "+ str(x['id'])+ ' from neighbors')
                toberemoved.append(x)
                continue
            else:
                newneighbors.append(x)
        self.neighbors = newneighbors
        for x in toberemoved:
            self.on_link_failure(x['id'])

    def shutEverythingDown(self, signal, frame):
        logger.debug("       huehuehue bye")
        sys.exit(0)

    def handleInterrupt(self, signal, frame):
        with open("interrupt_instruction.txt", 'r') as f:
            lines = f.readlines()
        interrupt_type = lines[0].strip()
        if interrupt_type == "sendmst":
            self.sendMSTInfos()
        elif interrupt_type == "removefromneighbors":
            self.removeFromNeighbors([l.strip() for l in lines[1:]])

    def startInterruptHandling(self):
        signal.signal(signal.SIGINT, self.handleInterrupt)
        signal.signal(signal.SIGTSTP, self.shutEverythingDown)

    def on_link_failure(self, lost_node_id):
        if self.parent != None and self.parent['id'] == lost_node_id:
            self.parent = None
        else:
            index = -1
            for i in range(len(self.children)):
                if self.children[i]['id'] == lost_node_id:
                    index = i
                    break
            if index >= 0:
                self.children.pop(index)
        msg = {'type': 'send_msg_to_root'}
        self.send_msg_to_root(msg)

    def send_msg_to_root(self, msg):
        logger.debug("send msg to root"+str(msg))
        if self.parent is None:
            self.on_broadcast_reiden()
        else:
            self.send_message(self.parent['ip'], self.parent['port'], msg)

    def broadcast_reiden(self, msg):
        logger.debug("broadcast rieden"+str(msg))
        if len(self.children) == 0:
            self.converge_cast_ack([])
        else:
            for child in self.children:
                self.send_message(child['ip'], child['port'], msg)

    def on_broadcast_reiden(self):
        msg = {'type': 'broadcast_reiden'}
        self.broadcast_reiden(msg)

    def broadcast_moe(self, msg):
        logger.debug("broADCAST MOE "+str(msg))
        self.fragmentId = msg['fragment_id']
        if len(self.children) == 0:
            edge = {'weight': sys.maxint}
            self.converge_cast_moe(edge, [])
        else:
            for child in self.children:
                self.send_message(child['ip'], child['port'], msg)

    def on_formation_completition(self):
        msg = {'type':'formation_completed',
        }
        self.broadcast_completion_info(msg)

    def broadcast_completion_info(self,msg):
        neighbours_info = {'type': 'neighbors_info',
                           'id': self.self_node['id'],
                           'parent':self.parent,
                           'children': self.children
        }
        self.send_message(self.master_node['ip'], self.master_node['port'], neighbours_info)
        for child in self.children:
            self.send_message(child['ip'], child['port'], msg)

    def on_broadcast_moe(self, list_of_node_ids):
        msg = {'type': 'broadcast_moe',
               'fragment_id': list_of_node_ids
               }
        self.broadcast_moe(msg)

    def handle_join(self, msg):
        self.join_request.append(msg['from'])
        if self.root_changed:
            self.root_changed = False
            self.join_request.remove(msg['from'])
            logger.debug("hua2")
            if msg['from']['id'] > self.self_node['id']:
                self.parent = msg['from']
            else:
                self.children.append(msg['from'])
                time.sleep(1)
                self.on_broadcast_reiden()
        pprint(vars(self))

    def change_root(self, path, child, edge):
        logger.debug("change root initiated"+str(path)+","+str(child)+","+str(edge))
        if len(path) == 1:
            # call the join function
            if child is not None:
                self.children.append(child)
            self.parent = None
            self.root_changed = True
            msg ={}
            msg['type'] = "join_request"
            msg['from'] = edge['inside']
            self.send_message(edge['outside']['ip'], edge['outside']['port'], msg)
            if edge['outside'] in self.join_request:
                self.root_changed = False
                self.join_request.remove(edge['outside'])
                logger.debug("hua1"+str(edge))
                if edge['outside']['id'] > edge['inside']['id']:
                    self.parent = edge['outside']
                else:
                    self.children.append(edge['outside'])
                    time.sleep(1)
                    self.on_broadcast_reiden()
            pprint(vars(self))
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
            msg['edge'] = edge
            self.send_message(self.parent['ip'], self.parent['port'], msg)

    def converge_cast_moe(self, edge, path):
        logger.debug("converge_cast_moe inititated"+str(edge)+","+str(path))
        self.ack += 1
        if hasattr(self, 'moeList'):
            self.moeList.append((edge, path))
        else:
            self.moeList = []
            self.moeList.append((edge, path))
        if self.ack >= len(self.children):
            self.ack = 0
            ans_path = []
            min_wt = sys.maxint
            min_edge = {}
            min_edge['weight'] = sys.maxint
            for anedge in self.moeList:
                if min_wt > anedge[0]['weight']:
                    min_wt = anedge[0]['weight']
                    min_edge = anedge[0]
                    ans_path = anedge[1]
            self.moeList = []
            own_moe = self.get_moe()
            if own_moe['weight'] != sys.maxint:
                if own_moe['weight'] < min_edge['weight']:
                    ans_path = [self.self_node]
                    min_edge = own_moe
                else:
                    ans_path.append(self.self_node)
            else:
                ans_path.append(self.self_node)
            if self.parent is not None:
                msg = {}
                msg['type'] = 'moe_update'
                msg['edge'] = min_edge
                msg['path'] = ans_path
                self.send_message(self.parent['ip'], self.parent['port'], msg)
            else:
                if min_edge['weight'] != sys.maxint:
                    self.change_root(ans_path, self.parent, min_edge)  # check this line
                else:
                    logger.debug("Tree sahi ho gaya huehuehuehue")
                    self.on_formation_completition()


    def get_moe(self):
        min_wt = sys.maxint
        min_edge = {}
        min_edge['weight'] = sys.maxint
        ### COnfirm neighbors
        for neighbor in self.neighbors:
            if neighbor['id'] not in self.fragmentId:
                if min_wt > neighbor['weight']:
                    min_wt = neighbor['weight']
                    min_edge['inside'] = self.self_node
                    nbr = {}
                    nbr['id'] = neighbor['id']
                    nbr['ip'] = neighbor['ip']
                    nbr['port'] = neighbor['port']
                    min_edge['outside'] = nbr
                    min_edge['weight'] = min_wt
        return min_edge

    def converge_cast_ack(self, subtreeId):
        logger.debug("converge_cast_ack initiated"+str(subtreeId))
        self.ack += 1
        if self.ack == 1:
            self.fragmentId = [self.self_node['id']]
        self.fragmentId.extend(subtreeId)
        if self.ack >= len(self.children):
            self.ack = 0
            if self.parent is not None:
                msg = {}
                msg['type'] = "ack_to_reiden"
                msg['msg'] = self.fragmentId
                self.send_message(self.parent['ip'], self.parent['port'], msg)
            else:
                # broadcast MOE and fragment message
                self.on_broadcast_moe(self.fragmentId)
