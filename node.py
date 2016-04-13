from transporter_api import Transporter
import networkx as nx
import json
from pprint import pprint

class Node(Transporter):
    def on_receive(self, msg):
        print "Received:", msg
        for m in msg:
            decoded_json = json.loads(m)
            type = decoded_json['type']
            if type == 'send_init_along_path':
                self.handleInitAlongPath(decoded_json)

    def handleInitAlongPath(self, msg):
        if len(msg['remaining_path']) > 0:
            ip, port = msg['remaining_path'][0]
            msg['remaining_path'].remove(msg['remaining_path'][0])
            self.send_message(ip, port, msg)
        else:
            self.self_node = msg['msg']['self_node']
            self.root_node = msg['msg']['root_node']
            self.fragmentId = set(msg['msg']['self_node']['id'])
            self.parent = msg['msg']['parent']
            self.children = msg['msg']['children']
            self.ack = 0
            pprint(vars(self))