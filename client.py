import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket
import sys
from threading import Thread 
import multiprocessing
import random

key_value_store = dict()
servers = dict()
my_port = ""

def connect_to_server(port):
    print ("### here ",port)
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
        print ("disconnect_server from client: ", port)
        servers.pop(port,None)

def today():
    today = datetime.datetime.today()
    return xmlrpc.client.DateTime(today)

def get(key):
    if len(servers) == 0:
        return "No server is connected"
    serv = random.randint(0,len(servers)-1)
    li = list(servers.values())
    val = li[serv].request("get "+str(key))
    print(val)
    return val

def put_value(key,value):
    if len(servers) == 0:
        return "No server is connected"
    serv = random.randint(0,len(servers)-1)
    li = list(servers.values())
    li[serv].request("put "+str(key)+" "+str(value))

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
    print ("here")
    try:
        my_port = id
        port = int(id)
    except:
        print("Give appropriate port number")
        sys.exit(-1)
    client = SimpleXMLRPCServer(("localhost", port))
    print("Listening on port "+str(port))
    client.register_function(today, "today")
    client.register_function(get, "get")
    client.register_function(put_value, "put_value")
    client.register_function(connect_to_server, "connect_to_server")
    client.register_function(disconnect_server, "disconnect_server")
    client.register_function(parse_req, "request")
    queue.put("Manu")
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

