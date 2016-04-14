import sys


def on_link_failure(self, lost_node_id):
    if self.parent['id'] == lost_node_id:
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
    if self.parent is None:
        self.on_broadcast_reiden()
    else:
        self.send_message(self.parent['ip'], self.parent['port'], msg)


def broadcast_reiden(self, msg):
    if len(self.children) == 0:
        ########################Check this function#######################
        self.converge_cast_ack([])
    else:
        for child in self.children:
            self.send_message(child['ip'], child['port'], msg)


def on_broadcast_reiden(self):
    msg = {'type': 'broadcast',
           'broadcast_type': 'reiden',
           }
    self.broadcast_reiden(msg)


def broadcast_moe(self, msg, list_of_node_ids):
    if len(self.children) == 0:
        edge = {'weight': sys.maxint}
        self.converge_cast_moe(edge, [])
    else:
        for child in self.children:
            self.send_message(child['ip'], child['port'], msg)


def on_broadcast_moe(self, list_of_node_ids):
    msg = {'type': 'broadcast',
           'broadcast_type': 'moe',
           'fragment_id': list_of_node_ids
           }
    self.broadcast_moe(msg, list_of_node_ids)
