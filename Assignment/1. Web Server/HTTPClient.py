from socket import *
import sys 

serverName = sys.argv[1]
serverPort = sys.argv[2]

fileName = sys.argv[3]

try:
	clientSocket = socket(AF_INET,SOCK_STREAM)
	clientSocket.connect((serverName,int(serverPort)))
	"""
	Request message format

	Method URL Version
	Host
	Connection
	User-agent
	Accept-language

	Example:
	GET /hello.html HTTP/1.1
	Host: xxxx
	Connection: Close / ?
	User-agent: Mozilla/ ?
	.
	.
	"""

	requestMsg = "Get /" + fileName + " HTTP/1.1\n"
	requestMsg += "Host: " + gethostbyname(serverName) + ":" + serverPort + "\n"
	requestMsg += "Connection: keep-alive"


	clientSocket.send(requestMsg.encode())
	while True:
		responseMessage = clientSocket.recv(1024)
		if(responseMessage):
			print("From server", responseMessage.decode())
		else:
			break
	
	clientSocket.close()
except:
	print("Error while connecting!")
	clientSocket.close()

