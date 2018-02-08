import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import xmlrpc.client
from threading import Thread 
import multiprocessing
import random


key_value_store = dict()
servers = dict()


def connect_to_server(port):
    print ("### here ",port)
    proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
    servers[port] = proxy

def disconnect_server(port):
    servers.pop(port,None)

def today():
    today = datetime.datetime.today()
    return xmlrpc.client.DateTime(today)



def get(key):
    serv = random.randint(0,len(servers))
    val = servers.values()[serv].request("get "+str(key))
    return val

def put_value(key,value):
    serv = random.randint(0,len(servers))
    servers.values()[serv].request("put "+str(key)+" "+str(value))


#parsing commands
# valid commands
# - put key value
# - get key
# - connect_to_client client_port
# - disconnect_client client_port

def parse_req(command):
    words = command.rstrip().split(" ")
    print(clients)
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

