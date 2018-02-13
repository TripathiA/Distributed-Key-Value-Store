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

servers = dict()
server_pid = dict()
clients = dict()

def joinServer(id):
	#server.start(id)
	queue = multiprocessing.Queue()
	proc = multiprocessing.Process(target=server.start, args=(id,queue,))
	proc.start()
	#proc = subprocess.Popen(["python3", "server.py",id,queue])
	obj = queue.get()
	print (obj)
	#proc.wait()
	server_pid[id] = proc.pid
	print("joinServer : "+id + " "+ str(proc.pid))
	proxy = xmlrpc.client.ServerProxy("http://localhost:"+id+"/")
	servers[id] = proxy
	#time.sleep(1)
	for s in servers:
		print(s,id,(s != id),servers[s])
		if(s != id):
			servers[s].request("connect_to_server "+id)
			servers[id].request("connect_to_server "+s)
	print("returning")

def killServer(id):
	os.kill(server_pid[id], signal.SIGKILL)
	print ("killServer : "+id+" "+str(server_pid[id]))

def joinClient(clientId, serverId):
	queue = multiprocessing.Queue()
	proc = multiprocessing.Process(target=client.start, args=(clientId,queue,))
	proc.start()
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
	clients[clientId].request("put "+str(key)+" "+str(value))

def get(clientId,key):
	val = clients[clientId].request("get "+str(key))
	print (val)

joinServer("8000")
joinServer("8001")
joinClient("8002","8000")
breakConnection("8002","8000")
createConnection("8000","8002")
createConnection("8002","8003")
put("8002",2,5)
get("8002",2)

