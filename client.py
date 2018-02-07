import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import xmlrpc.client
import random


servers = dict()

def get(key):
    serv = random.randint(0,len(servers))
    val = servers.values()[serv].request("get "+str(key))
    return val

def put_value(key,value):
    serv = random.randint(0,len(servers))
    servers.values()[serv].request("put "+str(key)+" "+str(value))

def connect_to_server(port):
    proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
    servers[port] = proxy

def disconnect_server(port):
    servers.pop(port,None)


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

