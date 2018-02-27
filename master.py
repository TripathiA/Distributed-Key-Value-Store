import server
import client
import subprocess
import sys
import os
import signal
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import time
import multiprocessing 
import json

servers = dict()
server_pid = dict()
clients = dict()
client_pid = dict()

def joinServer(id):
	#server.start(id)
	queue = multiprocessing.Queue()
	proc = multiprocessing.Process(target=server.start, args=(id,queue,))
	proc.start()
	#proc = subprocess.Popen(["python3", "server.py",id,queue])
	obj = queue.get()
	# print (obj)
	#proc.wait()
	server_pid[id] = proc.pid
	print("joinServer : "+id + " "+ str(proc.pid))
	proxy = xmlrpc.client.ServerProxy("http://localhost:"+id+"/")
	servers[id] = proxy
	#time.sleep(1)
	for s in servers:
		# print(s,id,(s != id),servers[s])
		if(s != id):
			servers[s].request("connect_to_server "+id)
			servers[id].request("connect_to_server "+s)

def killServer(id):
	for s in servers:
		servers[s].disconnect_server(id)
	for c in clients:
		clients[c].disconnect_server(id)
	print("Disconnected from all the servers")
	servers.pop(id)
	os.kill(server_pid[id], signal.SIGKILL)
	print ("killServer : "+id+" "+str(server_pid[id]))
	server_pid.pop(id)

def joinClient(clientId, serverId):
	queue = multiprocessing.Queue()
	proc = multiprocessing.Process(target=client.start, args=(clientId,queue,))
	proc.start()
	client_pid[clientId] = proc.pid
	obj = queue.get()
	print (obj)
	print("joinClient : "+ clientId + " "+ str(proc.pid))
	proxy = xmlrpc.client.ServerProxy("http://localhost:"+clientId+"/")
	clients[clientId] = proxy
	clients[clientId].request("connect_to_server "+serverId)

def breakConnection(id1,id2):
	if id1 in clients:
		clients[id1].request("disconnect_server "+id2)
	elif id2 in clients:
		clients[id2].request("disconnect_server "+id1)
	else:
		servers[id1].request("disconnect_server "+id2)
		servers[id2].request("disconnect_server "+id1)

def createConnection(id1,id2):
	if id1 in clients:
		clients[id1].request("connect_to_server "+id2)
	elif id2 in clients:
		clients[id2].request("connect_to_server "+id1)
	else:
		servers[id1].request("connect_to_server "+id2)
		servers[id2].request("connect_to_server "+id1)

def put(clientId,key,value):
	print ("put "+str(key)+" "+str(value)+ " "+str(clientId))
	clients[clientId].request("put "+str(key)+" "+str(value))

def get(clientId,key):
	print ("get "+str(key)+" "+str(clientId))
	val = clients[clientId].request("get "+str(key))
	print ("get of" + str(key) + " returns "+str(val))

def stabilize():
	for s in servers:
		print("do stabilize = "+s)
		servers[s].request("stabilize")
		print("stabilized = "+s)

def printStore(serverId):
	print("Kvstore for "+serverId)
	kvstore = json.loads(servers[serverId].request("get_kvstore"))
	for k in kvstore:
		print(k+" : "+str(kvstore[k][0]))
	# print(kvstore)

def call():
	servers["8000"].call_test("8000")

def parse_req(command):
    words = command.rstrip().split(" ")
    if (len(words) == 4):
        return json.dumps(globals()[words[0]](words[1],words[2],words[3]))
    elif (len(words) == 3):
        return json.dumps(globals()[words[0]](words[1],words[2]))
    elif (len(words) == 2):
        return json.dumps(globals()[words[0]](words[1]))
    else:
    	return json.dumps(globals()[words[0]]())

req = "inp"
while(req != ""):
	try:
	    req = input("")
	except EOFError:
		break
	ret = parse_req(req)
	    #ret = proxy.request(req + " " + str(timestamp))
	print(ret)

for id in server_pid:
	os.kill(server_pid[id], signal.SIGKILL)

for id in client_pid:
	os.kill(client_pid[id], signal.SIGKILL)

