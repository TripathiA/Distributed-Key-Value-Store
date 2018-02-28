# Distributed-Key-Value-Store

Students:
Aastha Tripathi - at36962, aastha
Amanda Austin - aja3575, ajaustin
Manu Viswanadhan - mv26898, manu

How to run:
python3 master.py < input.txt
where input.txt is a sequence of newline delineated commands from standard input ending with EOF.

Testing:
We wrote a input file which has series of commands which tests the scenarios like:
1. Simple execution of key value store where we do a bunch of "put" requests and call stabilize and then do bunch of "get" requests in a fully connected graph of servers.
2. Another testing was when we created graph of servers which is not fully connected by breaking connections. Then we do a bunch of "put" requests and call stabilize and then do bunch of "get" requests.
3. Then we created a partition in the graph, we put same keys with different values on both the partition, then did "get" before calling stabilize and after calling stabilize.
4. We also tested the case when a server is dead and stabilize is called.
5. We tested the case when one client is connected to multiple servers and is doing bunch of "put" and then "get" requests. This scenario also give "ERR_DEP" if the graph has parition or is not stabilize yet.

Protocol Description:
We implemented Server as multi threaded rpc server and client also as the rpc server. The Client is a server as the master will communicate with the Client. The Master implemented all the required APIs. The joinServer api, starts a separate process for the server at the given port. Similarly joinClient starts a separate process for the Client at the given port. The Master keeps tracks of all the Servers and Clients as a dictionary with entries as port as key and value the server object created in joinServer.

The Client mainatins its own key value store to maintain the information of timestamp associated to each key which it can use later to compare the updated values and a dictionary of all the servers it is connected to. If it gets a "get" request it randomly selects a server from the servers it is connected to and do a "get" request to that server. If a "put" request comes, it stores the given key value in its own key value store and do a "put" request to a randomly selected server. The client has its own key value store just to check if the value it is getting from server is more updated than itself or not. To connect to another server, the xmlrpc library connects to the server and store this connection instance in dictionary of servers. To disconnect a server, we just pop that server connection instance from the dictionary of servers.  

The Server mainatins its own key value store and a dictionary of all the servers it is connected to. If it gets a "get" request it returns the value from the key value store it has. If a "put" request comes, it stores the given key value in its own key value store and pass on the values to other neighbouring servers as a part of gossip protocol. To connect to another server, the xmlrpc library make the one server as client and connects to the server and store this connection instance in dictionary of servers. To disconnect a server, we just pop that server connection instance from the dictionary of servers.  

For the stabilize call, the master calls stabilize to every server sequentially.
Once a server receives the stabilize() call, it starts informing its neighbors ( provided the server is not stabilized yet) by calling their stabilize function. There are logical checks in place to ensure that cycles are not formed by new servers initiating stabilize of the severs who are already in the middle of stabilize. This leads to a minimal spanning tree with a parent and children nodes. The stabilize function will wait till the children have gathered updated information of the kv store from all it’s children. This way the information is percolated upwards and the root of the tree ( the server called by the master) will have the updated information of all the nodes of its partition. Now the root will broadcast the kv store to its children in the MST, and the information will reach till its leaves. Once the broadcast is completed, all the nodes in the tree will mark themselves as stabilized, and hence will not take part in the process when the master calls their api. 
This way for every partition a MST will be formed and the information passed among the nodes.

Eventual consistency and session guarantees are obtained through the use of Lamport clocks. Each server and client keeps a logical clock that is incremented on each event. When a server stores a value in its key-value store, it stores its current timestamp along with its ID in order to break ties in timestamps. When a client requests a value, it compares the timestamp of the value it receives from the server with the timestamp of the last value it put or got from the server to ensure monotonic reads and read-after-write consistency. Upon a stabilize call, servers compare the timestamps and IDs of all of their values in their key-value store to ensure that the latest value is the one that is kept.
 

