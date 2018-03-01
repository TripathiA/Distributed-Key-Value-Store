# Distributed-Key-Value-Store

## Students:

Aastha Tripathi - at36962, aastha

Amanda Austin - aja3575, ajaustin

Manu Viswanadhan - mv26898, manu

## How to run:
Our implementation can be run with the following command:

    python3 master.py < input.txt

where input.txt is a sequence of newline delineated commands from standard input in the form:

    commandName arg1 arg2 ...
    
An example command:

    put 8021 18 80
    
This tells a client with ID 8021 to request a put of value 80 in key 18.

## Testing:

We wrote a input file which has series of commands which tests different scenarios such as:
1. Simple execution of key-value store with a bunch of put requests, a call to stabilize, and a bunch of get requests in a fully connected graph of servers.
2. Disconnecting some servers to create a non fully connected graph and perform a series of put requests, get requests, and stabilize calls.
3. Disconnecting some servers to create a partition and perform put requests in both partitions, then some get requests, and a call to stabilize. Next, a connection is restored to remove the partition, a put request is performed, followed by a get, and then a stabilize.
4. Killing a server
5. Starting a new server
6. Connecting a client to multiple servers in various scenarios
7. Issuing concurrent put requests followed by concurrent get requests in various scenarios
8. Issuing a series of put requests, followed by a stabilize, then a series of get requests, and measuring the execution time

## Protocol Description:

We implemented the server using a multi-threaded RPC server and the client as a single-threaded RPC server. The master implemented all the required APIs and issues commands to servers and clients to perform. The joinServer API starts a separate process for the server at the given port. Similarly, joinClient starts a separate process for the client at the given port. The master keeps track of all the servers and clients, killing the processes when it has finished executing the series of commands.

Eventual consistency and session guarantees are obtained through the use of Lamport clocks. All servers and clients keep a logical clock that is incremented on each event. When a server stores a value in its key-value store, it also stores its current timestamp along with its ID in order to break ties in timestamps. When a client requests a value, it compares the timestamp of the value it receives from the server with the timestamp of the last value it put or got from the server to ensure monotonic reads and read-after-write consistency. Upon a stabilize call, servers compare the timestamps and IDs of all of their values in their key-value store to ensure that the latest value is the one that is kept.

Each client maintains a dictionary of servers it is connected to. To perform a put request, a client randomly selects a server from the connected servers from which to get the value. A put request is handled in a similar way. The client keeps a memory of the put and get results it has done in order to ensure the session guarantees. If a received value from a server has an earlier timestamp than the last value the client put in that key, then ERR_DEP is returned. Otherwise, the client knows that the value is at least as recent as the last value it put or received from a server, so it returns that value. If a client requests a value but a server does not have the key, then one of two things can happen. If the client previously wrote a value to that key, then ERR_DEP is returned. Otherwise ERR_KEY is returned.

Each server maintains its own key-value store and a dictionary of all the servers it is connected to. If the server receives a get request, it returns the value from the its own key-value store. If it gets a put request, it stores the given key-value pair in its own key-value store and passes on the values to other neighboring servers as a part of gossip protocol.

For the stabilize call, the master calls stabilize for each server in sequence. Once a server receives the stabilize call, it starts informing its neighbors (provided the server is not already stabilized) by calling their stabilize procedure. Logical checks are done to ensure that cycles are not formed by new servers initiating stabilize of the severs that are already in the middle of stabilize. This leads to a minimal spanning tree (MST) with a parent and children nodes. The stabilize function will wait until the children have gathered updated information of the key-value stores from all their children. In this way, the information is percolated upwards and the root of the tree (the server called by the master) will have the updated information of all the nodes of its partition. Now the root will broadcast the key-value store to its children in the MST, and the children will set this key-value store as their own. Once the broadcast is completed, all the nodes in the tree will mark themselves as stabilized, and hence will not take part in the process again for this round of stabilization. 
 
