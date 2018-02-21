import xmlrpc.client
import datetime
import sys

port = sys.argv[1]
proxy = xmlrpc.client.ServerProxy("http://localhost:"+port+"/")
timestamp = 1

while True:
    req = input("Request ? ")
    timestamp += 1
    print(req)
    ret = proxy.request(req + " " + str(timestamp))
    print(ret)
