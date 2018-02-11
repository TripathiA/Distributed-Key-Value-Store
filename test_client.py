import xmlrpc.client
import datetime
import sys

port = sys.argv[1]
proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")

while True:
	req = input("Request ? ")
	print(req)
	ret = proxy.request(req)
	print(ret)
