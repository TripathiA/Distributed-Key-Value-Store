import datetime
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import socket
import sys
from threading import Thread 
import multiprocessing
import random
import json
import socketserver

key_value_store = dict()
servers = dict()
my_port = ""
timestamp = 1

class AsyncXMLRPCServer(socketserver.ThreadingMixIn,SimpleXMLRPCServer): pass

def connect_to_server(port):
    if(port == my_port):
        return "Not a valid server port"
    proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
    try:
        proxy._()   # Call a fictive method.
    except xmlrpc.client.Fault:
        servers[port] = proxy
    except socket.error:
        # Not connected ; socket error mean that the service is unreachable.
        return 

    

def disconnect_server(port):
    if(port in servers):
        #print ("disconnect_server from client: ", port)
        servers.pop(port,None)
    return ""

def today():
    today = datetime.datetime.today()
    return xmlrpc.client.DateTime(today)

def get(key):
    global timestamp
    if len(servers) == 0:
        return "No server is connected"
    serv = random.randint(0,len(servers)-1)
    li = list(servers.values())
    val = json.loads(li[serv].request("get "+str(key) + " " + str(timestamp)))
    #print("getting value from server: "+str(li[serv]))
    #print("got: "+str(val))
    old_timestamp = timestamp
    timestamp = max(timestamp, val[1]) + 1
    if val[0] == "ERR_KEY":
        # server thinks it doesn't have this key - did we ask for it before?
        if key in key_value_store:
            # we asked for it before so return "ERR_DEP"
            return "ERR_DEP"
        else:
            # we did not ask for it before, so we can return "ERR_KEY"
            return "ERR_KEY"
    else:
        # server had the key, did we previously know about this key?
        if key in key_value_store:
            # we knew about this key already, so check the timestamp
            if key_value_store[key][1] > val[1]:
                # timestamp from the server is less than the timestamp
                # we previously knew, so return ERR_DEP
                return "ERR_DEP"
            else:
                # timestamp is newer, so update our memory of k-v pairs
                # and return value from server
                key_value_store[key] = val
                return val[0]
        else:
            # we learned about a new key, so update our memory of k-v pairs
            # and return value from server
            key_value_store[key] = val
            # print("val: "+val[0])
            return val[0]

def put_value(key,value):
    global timestamp
    if len(servers) == 0:
        return "No server is connected"
    serv = random.randint(0,len(servers)-1)
    li = list(servers.values())
    val = json.loads(li[serv].request("put "+str(key)+" "+str(value) + " " + str(timestamp)))
    #print("putting value to server: "+str(li[serv]))
    # remember the value and timestamp of what the server put
    # print("value from server: "+str(val))
    timestamp = max(timestamp, int(val[1])) + 1
    key_value_store[key] = val
    

#parsing commands
# valid commands
# - put key value
# - get key
# - connect_to_client client_port
# - disconnect_client client_port

def parse_req(command):
    words = command.rstrip().split(" ")
    if("put" in words[0]):
        val = put_value(words[1],words[2])
        return ""+str(val)
    else:
        return ""+str(globals()[words[0]](words[1]))

def threaded_function(arg) :
    arg.serve_forever()

def start(id,queue):
    global my_port
    try:
        my_port = id
        port = int(id)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    client = AsyncXMLRPCServer(("localhost", port),SimpleXMLRPCRequestHandler, logRequests=False)
    print("Listening on port "+str(port))
    client.register_function(today, "today")
    client.register_function(get, "get")
    client.register_function(put_value, "put_value")
    client.register_function(connect_to_server, "connect_to_server")
    client.register_function(disconnect_server, "disconnect_server")
    client.register_function(parse_req, "request")
    queue.put("Done")
    client.serve_forever()

    
if __name__== "__main__":
    try:
        port = int(sys.argv[1])
        my_port = str(port)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    server = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    server.register_function(get, "get")
    server.register_function(put_value, "put_value")
    server.register_function(connect_to_server, "connect_to_server")
    server.register_function(disconnect_server, "disconnect_server")
    server.register_function(parse_req, "request")
    server.serve_forever()

