from socket import *
import sys 

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
serverSocket.bind(('',6789))
serverSocket.listen(1)
while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr =  serverSocket.accept()          
    try:
        '''
        print out the request message
        GET /hello.html HTTP/1.1
        Host: 127.0.1.1:6789
        Connection: keep-alive 
        ..
        .
        .
        '''
        message =  connectionSocket.recv(1024).decode()               
        print(message)

        '''
        Get the file name from the request message
        message.split() to become
        ['GET', '/hello.html', 'HTTP/1.1', 'Host:' , .... ]
        Hence, message.split()[1] to get /hello.html
        '''

        filename = message.split()[1]                 
        f = open(filename[1:])                        
        outputdata = f.readlines()                   

        #Send one HTTP header line into socket
        header = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
        connectionSocket.send(header.encode())

        #Send the content of the requested file to the client

        for i in range(0, len(outputdata)):           
            print(outputdata[i])
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        
        connectionSocket.close()
        # break
    except IOError:
        #Send response message for file not found
        error = "HTTP/1.1 404 Not Found\r\n"
        connectionSocket.send(error.encode())
        #Close client socket
        connectionSocket.close()


serverSocket.close()

sys.exit()#Terminate the program after sending the corresponding data