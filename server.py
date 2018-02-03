import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import xmlrpc.client
from threading import Thread 
import multiprocessing


key_value_store = dict()
servers = dict()


def get(key,distribute=True):
    curr = key_value_store[key][1]
    ret = key_value_store[key]
    if distribute:
        for s in servers:
            val = servers[s].get(key,False)
            if(val[1] > curr):
                ret = val
                key_value_store[key] = val
    print("val "+str(key_value_store))
    return key_value_store[key]

def put_value(key,value):
    if(key in key_value_store):
        key_value_store[key] = [value,key_value_store[key][1]+1]
    else:
        key_value_store[key] = [value,1]

def connect_to_server(port):
    print ("###",port)
    proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
    servers[port] = proxy

def disconnect_server(port):
    servers.pop(port,None)

def today():
    today = datetime.datetime.today()
    return xmlrpc.client.DateTime(today)

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
        put_value(words[1],words[2])
        return "Inserted the value"
    else:
        return "Return: "+str(globals()[words[0]](words[1]))

def threaded_function(arg) :
    arg.serve_forever()

def start(id,queue):
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
    try:
        port = int(sys.argv[1])
        queue = sys.argv[2]
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
    thread = Thread(target = threaded_function, args= (server,))
    thread.start()
    queue.put("Manu")
    # server.serve_forever()


