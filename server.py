import datetime
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import sys
import xmlrpc.client
import threading 
import multiprocessing
import json
import socketserver

#stabilize
#try except if not key available
#try except for server not available 

class AsyncXMLRPCServer(socketserver.ThreadingMixIn,SimpleXMLRPCServer): pass

key_value_store = dict()
servers = dict()
my_port = ""
stabilized = False
sent = False
timestamp = 1
Threads = dict()
lock = threading.Lock()


def get(key, client_timestamp):
    global timestamp
    curr = -1
    ret = ["ERR_KEY", timestamp, my_port]
    timestamp = max(timestamp, int(client_timestamp)) + 1
    if key in key_value_store:
        ret = key_value_store[key]
    return ret

def put_gossip(key, value, other_timestamp, port):
    global timestamp
    # called from another server, so check timestamps before updating our k-v store
    if key not in key_value_store or timestamp < other_timestamp or (timestamp == other_timestamp and my_port < port):
        # either a new key or a newer value for a key we already know about
        # with ties broken by server id
        key_value_store[key] = [value, other_timestamp, port]
    # either way, advance our clock
    timestamp = max(timestamp, int(value[1])) + 1
    print("hereeee"+port)
    return "hi"
    

def put_value(key, value, client_timestamp):
    global timestamp
    # called from a client, so we must update the k-v store
    # and tell our neighbours
    timestamp = max(timestamp, int(client_timestamp)) + 1
    key_value_store[key] = [value, timestamp, my_port]
    
    for s in servers:
        print("calling: "+s)
        servers[s].put_gossip(key, value, int(timestamp), my_port)
        print("hereeee#"+my_port)
	# return value put to the client
    return key_value_store[key]

def connect_to_server(port):
    if(port == my_port):
        return "Not a valid port"
    print ("###",port)
    proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
    servers[port] = proxy

def disconnect_server(port):
    print ("disconnect_server: ", port)
    servers.pop(port,None)

def today():
    today = datetime.datetime.today()
    return xmlrpc.client.DateTime(today)

def get_kvstore():
    return key_value_store

def get_stabilize_state():
    return stabilized

def set_stabilize_state(val):
    stabilized = val

def set_sent_state(val):
    sent = val

def get_sent_state():
    return sent

def set_kvstore(kvstore):
    key_value_store = kvstore

def set_stab_kvstore(kvstore):
    global stabilized
    if stabilized:
        return ""
    stabilized = True
    key_value_store = kvstore;
    for s in servers:
        servers[s].set_stab_kvstore(key_value_store)
    return ""

def acc_kvstore(port,calling_ports):    
    calling_ports.append(my_port)
    print("acc_kv: "+my_port+" "+port+" "+str(calling_ports))
    kvstore = servers[port].stabilize(False,calling_ports)
    if kvstore:
        for key in kvstore:
            if ((key not in key_value_store) or (key in key_value_store and kvstore[key][1] > key_value_store[key][1])):
                key_value_store[key] = kvstore[key]
    return ""

def dist_kvstore(args):
    servers[args].set_stab_kvstore(key_value_store)
    return ""

def stabilize(source = True,calling_ports=[my_port]):
    global Threads, stabilized, sent
    print("var val: "+str(my_port)+" "+str(source)+" "+str(sent)+" "+str(stabilized)+" "+str(calling_ports))
    if stabilized:
        sent = False
        stabilized = False
        print("return none s: "+my_port)
        return ""
    lock.acquire()
    if sent:
        lock.release()
        print("return none: "+my_port)
        return ""
    else:
        sent = True;
    lock.release()

    for s in servers:
        if(s not in calling_ports):
            print("on: "+my_port+" "+s)
            t = threading.Thread(target=acc_kvstore,args=(s,calling_ports))
            Threads[s] = t
            Threads[s].start()
            print("thread spawned: "+s)
        # kvstore = servers[s].stabilize(False)
        # if kvstore:
        #     for key in kvstore:
        #         if ((key not in key_value_store) or (key in key_value_store and kvstore[key][1] > key_value_store[key][1])):
        #             key_value_store[key] = kvstore[key]
    for t in Threads:
        Threads[t].join()
    Threads.clear()
    if source == False:
        return key_value_store
    else:
        for s in servers:
            if(s not in calling_ports):
                Threads[s] = threading.Thread(target=dist_kvstore,args=(s,))
                Threads[s].start()
    for t in Threads:
        Threads[t].join()
    stabilized = False
    # sent = False
    return key_value_store

# def stabilize():
#     for s in servers:
#         kvstore = servers[s].get_kvstore()
#         for key in kvstore:
#             if ((key not in key_value_store) or (key in key_value_store and kvstore[key][1] > key_value_store[key][1])):
#                 key_value_store[key] = kvstore[key]
#     for s in servers:
#         servers[s].set_kvstore(key_value_store)

#parsing commands
# valid commands
# - put key value
# - get key
# - connect_to_server server_port
# - disconnect_server server_port

def call_test(id):
    for s in servers:
        print("hello "+my_port+" "+id)
        servers[s].call_test(my_port)
    return "bdbkvs"

def parse_req(command):
    words = command.rstrip().split(" ")
    print(servers)
    if("put" in words[0]):
        val = put_value(words[1],words[2],words[3])
        print("in: "+str(val))
        val1 = json.dumps(val)
        return val1
    # elif ("stabilize" in words[0]):
    #     return json.dumps(stabilize())
    else:
        if (len(words) == 3):
            return json.dumps(globals()[words[0]](words[1],words[2]))
        elif (len(words) == 2):
            return json.dumps(globals()[words[0]](words[1]))
        else:
            return json.dumps(globals()[words[0]]())

def threaded_function(arg) :
    arg.serve_forever()

def start(id,queue):
    global my_port
    my_port = id
    print ("here")
    try:
        port = int(id)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    server = AsyncXMLRPCServer(("localhost", port),SimpleXMLRPCRequestHandler)
    #server = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    server.register_multicall_functions()
    server.register_function(today, "today")
    server.register_function(get, "get")
    server.register_function(put_gossip, "put_gossip")
    server.register_function(put_value, "put_value")
    server.register_function(connect_to_server, "connect_to_server")
    server.register_function(disconnect_server, "disconnect_server")
    server.register_function(stabilize,"stabilize")
    server.register_function(parse_req, "request")
    server.register_function(set_stab_kvstore,"set_stab_kvstore")
    server.register_function(call_test, "call_test")
    # thread = Thread(target = threaded_function, args= (server,))
    # thread.start()
    queue.put("Manu")
    server.serve_forever()


if __name__== "__main__":
    id = sys.argv[1]
    global my_port
    my_port = id
    print ("here")
    try:
        port = int(id)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    server = AsyncXMLRPCServer(("localhost", port),SimpleXMLRPCRequestHandler)
    #server = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    server.register_multicall_functions()
    server.register_function(today, "today")
    server.register_function(get, "get")
    server.register_function(put_gossip, "put_gossip")
    server.register_function(put_value, "put_value")
    server.register_function(connect_to_server, "connect_to_server")
    server.register_function(disconnect_server, "disconnect_server")
    server.register_function(stabilize,"stabilize")
    server.register_function(parse_req, "request")
    server.register_function(set_stab_kvstore,"set_stab_kvstore")
    server.register_function(call_test, "call_test")
    # thread = Thread(target = threaded_function, args= (server,))
    # thread.start()
    #queue.put("Manu")
    server.serve_forever()
