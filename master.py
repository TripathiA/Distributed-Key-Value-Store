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
	#proc = subprocess.Popen(["python3", "server.py",id,queue])
	obj = queue.get()
	print (obj)
	#proc.wait()
	#client_pid[id] = proc.pid
	print("joinClient : "+ clientId + " "+ str(proc.pid))
	proxy = xmlrpc.client.ServerProxy("http://localhost:"+clientId+"/")
	clients[clientId] = proxy
	servers[serverId].request("connect_to_server"+clientId)
	clients[clientId].request("connect_to_client"+serverId)


joinServer("8000")
joinServer("8001")
joinClient("8002","8000")

