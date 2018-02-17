import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import xmlrpc.client
from threading import Thread 
import multiprocessing


#stabilize
#try except if not key available
#try except for server not available 


key_value_store = dict()
servers = dict()
my_port = ""
stabilized = False
sent = False
timestamp = 1

def get(key):
    curr = -1
    ret = [ERR_KEY, timestamp, my_port]
    timestamp += 1
    if key in key_value_store:
        ret = key_value_store[key]
    print("val "+ ret)
    return ret

def put_value(key,value, distribute = True):
    # was this called from a client or another server?
    if distribute:
        # called from a client, so we must update the k-v store
        # and tell our neighbours
        timestamp += 1
        key_value_store[key] = [value, timestamp, my_port]
        
        for s in servers:
            servers[s].put[key, [value, timestamp, my_port], False]
            
        return key_value_store[key]
    else:
        # called from another server, so check timestamps before updating our k-v store
        if key not in key_value_store or timestamp < value[1] or (timestamp == value[1] and my_port < value[2]):
                # either a new key or a newer value for a key we already know about
                # with ties broken by server id
                key_value_store[key] = [value[0], value[1], value[2]]
        # either way, advance our clock
        timestamp = max(timestamp, value[1]) + 1
        
    '''
    if(key in key_value_store) and timestamp > key_value_store[key][1]:
        key_value_store[key] = [value, timestamp, my_port]
    else:
        key_value_store[key] = [value,timestamp, my_port]
        
    if distribute:
        for s in servers:
            val = servers[s].put(key, value, False)
            if(val[1] > curr):
                ret = val
                key_value_store[key] = val
    return key_value_store[key]
    '''

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
    if stabilized:
        return
    stabilized = True
    key_value_store = kvstore;
    for s in servers:
        servers[s].set_stab_kvstore(key_value_store)

def stabilize(source = True):
    if stabilized:
        stabilized = False
        return None
    if sent:
        return None
    sent = True;
    for s in servers:
        kvstore = servers[s].stabilize(False)
        if kvstore:
            for key in kvstore:
                if ((key not in key_value_store) or (key in key_value_store and kvstore[key][1] > key_value_store[key][1])):
                    key_value_store[key] = kvstore[key]
    if source == False:
        return key_value_store
    else:
        for s in servers:
            servers[s].set_stab_kvstore(key_value_store)
    stabilized = False
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

def parse_req(command):
    words = command.rstrip().split(" ")
    print(servers)
    if("put" in words[0]):
        val = put_value(words[1],words[2])
        return ""+str(val)
    else:
        return ""+str(globals()[words[0]](words[1]))

def threaded_function(arg) :
    arg.serve_forever()

def start(id,queue):
    global my_port
    my_port == id
    print ("here")
    try:
        port = int(id)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    server = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    server.register_function(today, "today")
    server.register_function(get, "get")
    server.register_function(put_value, "put_value")
    server.register_function(connect_to_server, "connect_to_server")
    server.register_function(disconnect_server, "disconnect_server")
    server.register_function(parse_req, "request")
    # thread = Thread(target = threaded_function, args= (server,))
    # thread.start()
    queue.put("Manu")
    server.serve_forever()


if __name__== "__main__":
    print("starting server...")
    try:
        port = int(sys.argv[1])
        my_port = str(port)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    print("setting up port...")
    server = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    server.register_function(today, "today")
    server.register_function(get, "get")
    server.register_function(put_value, "put_value")
    server.register_function(connect_to_server, "connect_to_server")
    server.register_function(disconnect_server, "disconnect_server")
    server.register_function(parse_req, "request")
    server.serve_forever()

