from socket import *
from datetime import datetime
import time
import statistics


serverName = 'localhost'
serverPort = 12000
packetRTT = []

clientSocket = socket(AF_INET,SOCK_DGRAM)

for x in range(10):
	now = datetime.now()
	ping = "Ping " + str(x + 1) + " " + now.strftime("%H:%M:%S")
	startTime = time.process_time()

	clientSocket.sendto(ping.encode(),(serverName,serverPort))
	clientSocket.settimeout(1)

	try:
		returnedMsg, sererAddrs = clientSocket.recvfrom(2048)

		endTime = time.process_time()
		rtt = "{:.5f}".format(endTime - startTime)
		packetRTT.append(float(rtt))

		print(returnedMsg.decode() + " " , rtt + " ms")
	except timeout:
		print("Request" , x + 1, "timed out")

clientSocket.close()

packet_loss = 100 * (len(packetRTT) / 10)
print("{} packets sent, {} received, {}% packet loss".format(10, len(packetRTT), 100.0 - packet_loss))
print("Min rtt = {:.5f} Avg rtt = {:.5f} Max rtt = {:.5f} ms".format(min(packetRTT), statistics.median(packetRTT), max(packetRTT)))


