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
# convert the ISO8601 string to a datetime object
# converted = datetime.datetime.strptime(today.value, "%Y%m%dT%H:%M:%S")
# print("Today: %s" % converted.strftime("%d.%m.%Y, %H:%M"))