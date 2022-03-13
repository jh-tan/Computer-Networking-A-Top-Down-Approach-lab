from socket import *
import threading

class ThreadedServer:
	def __init__(self):
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.bind(('',6789))

	def listen(self):
		self.sock.listen(10)
		while True:
			connectionSocket, addr =  self.sock.accept()          
			t = threading.Thread(target=self.processRequest, name='requestThread', args=(connectionSocket,addr)).start()

	def processRequest(self,socket,addr):
		try:
			message =  socket.recv(1024).decode()               
			print(message)

			filename = message.split()[1]                 
			f = open(filename[1:])                        
			outputdata = f.readlines()                   

			header = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
			socket.send(header.encode())


			for i in range(0, len(outputdata)):           
				print(outputdata[i])
				socket.send(outputdata[i].encode())
			socket.send("\r\n".encode())

			socket.close()
		except IOError:
			error = "HTTP/1.1 404 Not Found\r\n"
			socket.send(error.encode())
			socket.close()

if __name__ == "__main__":
	ThreadedServer().listen()

