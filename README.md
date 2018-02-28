# Distributed-Key-Value-Store

Implementation of Distributed Key Value Store. RPC connection between servers and between server and client.

To run server:
python server.py <port_number>

To run client:
python client.py <port_number> 
The client is implemented as a server for Master to communicate to the same.






Stabilize - 
The master calls stabilize to every server sequentially.
Once a server receives the stabilize() call, it starts informing its neighbors ( provided the server is not stabilized yet) by calling their stabilize function. There are logical checks in place to ensure that cycles are not formed by new servers initiating stabilize of the severs who are already in the middle of stabilize. This leads to a minimal spanning tree with a parent and children nodes. The stabilize function will wait till the children have gathered updated information of the kv store from all it’s children. This way the information is percolated upwards and the root of the tree ( the server called by the master) will have the updated information of all the nodes of its partition. Now the root will broadcast the kv store to its children in the MST, and the information will reach till its leaves. Once the broadcast is completed, all the nodes in the tree will mark themselves as stabilized, and hence will not take part in the process when the master calls their api. 
This way for every partition a MST will be formed and the information passed among the nodes.

