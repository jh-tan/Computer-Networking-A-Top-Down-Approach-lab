import base64
from socket import *
import ssl
import getpass
import time



# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = "smtp.gmail.com"

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((mailserver,587))

recv = clientSocket.recv(1024).decode()
print(recv)

if recv[:3] != '220':
	print('220 reply not received from server.')

# Send HELO command and print server response.
# Send EHLO command for SMTP or TLS / SSL
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')


# Start TLS command 
clientSocket.send("STARTTLS\r\n".encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)

clientSocket = ssl.wrap_socket(clientSocket)

# Server will reply 334 VXNlcm5hbWU6
# VXNlcm5hbWU6 is base64 encoded format, after decode it , VXNlcm5hbWU6 => Username:
command = 'AUTH LOGIN\r\n'
clientSocket.send(command.encode())
resp = clientSocket.recv(1024)
print (resp.decode())


# In order to work for gmail, have to go to gmail account setting -> security -> enable 'Less secure app access'
# But 'Less secure app access' will no longer be available on 30, May 2022
command = base64.b64encode(str(input("Enter the email address")).encode())
clientSocket.send((command.decode()+"\r\n").encode())
resp = clientSocket.recv(1024)
print (resp.decode())


# After enter the username / email address, server will response 334 UGFzc3dvcmQ6
# Which UGFzc3dvcmQ6 => Password:
command = base64.b64encode(str(getpass.getpass("Password: ")).encode())
clientSocket.send((command.decode()+"\r\n").encode())
resp = clientSocket.recv(1024)
print (resp.decode())

# Send MAIL FROM command and print server response.
mailFromCommand = 'MAIL FROM: <a175391@siswa.ukm.edu.my>\r\n' 
clientSocket.send(mailFromCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# Send RCPT TO command and print server response. 
mailFromCommand = 'RCPT TO: <holygaming00@gmail.com>\r\n' 
clientSocket.send(mailFromCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1 )
if recv1[:3] != '250':
    print('250 reply not received from server.')


# Send DATA command and print server response. 
mailFromCommand = 'DATA\n' 
clientSocket.send(mailFromCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)

if recv1[:3] != '354':
    print('250 reply not received from server -- 1')

# Send message data.

# Have to state the headers for gmail 
mailFromCommand = 'From: test <"Change to the sender email address">\r\n'
clientSocket.send(mailFromCommand.encode())

mailFromCommand = 'To: "Change to the receiver email address"\r\n' 
clientSocket.send(mailFromCommand.encode())

mailFromCommand = 'Date: ' + time.asctime( time.localtime(time.time()) ) + '\r\n'
clientSocket.send(mailFromCommand.encode())

mailFromCommand = 'Subject: Email subject here\r\n' 
clientSocket.send(mailFromCommand.encode())
clientSocket.send('\r\n'.encode())
clientSocket.send("Email content here\r\n".encode())


# Message ends with a single period.
mailFromCommand = '.\r\n' 
clientSocket.send(mailFromCommand.encode())

# Send QUIT command and get server response.
mailFromCommand = 'QUIT\r\n' 
clientSocket.send(mailFromCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)