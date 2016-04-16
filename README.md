# Replication Topology Maintenance

There exists a main client which contains a command line util that allows the user to specify the network topology and constraints.
The user will need to specify the information about the distributed network, ie the number of nodes, the physical edges and their costs (bandwidths).
The user also specifies the replication information i.e. information about nodes replicating from which other nodes.
The user can further provide the following constraints which will be used for the initial spanning tree construction:
Specify a degree bound in the spanning tree to be constructed (replication topology)
Specify the links which should always be a part of the spanning tree.
Restrict maximum number of hops required between any two nodes replicating each other to be less than a given threshold.

Master server: 
Is used for taking user inputs mentioned above.
Initially generates the spanning tree or the replication topology using the constraints specified.
Communicates information about the constructed spanning tree to each node in the network.
Will update the topology in case of user specified changes like addition/deletion of links in the current topology.
Gets the update about the replication topology changes on failure of links/nodes. 

Link/Node failure: Two nodes get alerted and they notify the master server about the failure. Master will check whether the nodes had a direct edge in the existing spanning tree. If there it is a link failure else a node failure.

Workflow:
Master server takes input from user.
Initial spanning tree is constructed.
Allow the user to view the constructed spanning tree and specify further constraints. 
On addition/deletion of a node/link replication is frozen via flooding, and a distributed spanning tree algorithm is run to reconstruct a spanning tree.
Master is then notified of the topology changes using convergecast. 



