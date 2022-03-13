from pickle import bytes_types
import re
from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8


class ICMPPinger:
    def __init__(self, target_ip, timeout):
        self.timeout = timeout
        self.icmp_seq = 1
        try:
            self.target_ip = gethostbyname(target_ip)
        except:
            print("Temporary failure in name resolution")

    def checksum(self, string):
        csum = 0
        countTo = (len(string) // 2) * 2
        count = 0

        while count < countTo:
            thisVal = ord(string[count + 1]) * 256 + ord(string[count])
            csum = csum + thisVal
            csum = csum & 0xFFFFFFFF
            count = count + 2

        if countTo < len(string):
            csum = csum + ord(string[len(string) - 1])
            csum = csum & 0xFFFFFFFF

        csum = (csum >> 16) + (csum & 0xFFFF)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xFFFF
        answer = answer >> 8 | (answer << 8 & 0xFF00)
        return answer

    def receiveOnePing(self, mySocket, ID, timeout, destAddr):
        timeLeft = timeout

        while 1:
            startedSelect = time.time()
            whatReady = select.select([mySocket], [], [], timeLeft)
            howLongInSelect = time.time() - startedSelect
            if whatReady[0] == []:  # Timeout
                return "Request timed out."

            timeReceived = time.time()
            recPacket, addr = mySocket.recvfrom(1024)
            # print("4 " ,recPacket) # Debug use

            # Fetch the ICMP header from the IP packet
            """
            This is the simplication of ICMP which does not follow the official specification in RFC 1739
            The ICMP header starts after bit 160 of the IP header 
            ICMP_REQUEST_TYPE = 160 bit to 167 bit
            ICMP_REQUEST_CODE = 168 bit to 175 bit
            ICMP_CHECKSUM     = 176 bit to 191 bit
            ICMP_ID           = 192 bit to 207 bit
            ICMP_SEQUENCE     = 208 bit to 223 bit
            1 byte 8 bit, 160 / 8 = 20. Thats why recPacket start from 20 and end at 28 [20:28]
            """
            (
                ICMP_request_type,
                ICMP_request_code,
                ICMP_checksum,
                ICMP_id,
                ICMP_sequence,
            ) = struct.unpack("bbHHh", recPacket[20:28])
            SOURCE_IP_ADDRESS = map(str, struct.unpack("BBBB", recPacket[12:16]))
            SOURCE_IP_ADDRESS = ".".join(SOURCE_IP_ADDRESS)
            HOSTNAME = gethostbyaddr(SOURCE_IP_ADDRESS)[0]
            IP_TTL, = struct.unpack("b",recPacket[8:9])
            ICMP_SENDING_TIME, = struct.unpack("d",recPacket[28:])

            time_diff = (timeReceived - ICMP_SENDING_TIME )* 1000
            responseMsg = "{} bytes from {} ({}): ".format(
                    len(bytearray(recPacket)[20:28]), HOSTNAME, SOURCE_IP_ADDRESS
                )
            responseMsg += "icmp_seq={} ".format(ICMP_sequence)
            responseMsg += "ttl={} ".format(IP_TTL)
            responseMsg += "time={0:.3g} ms".format(time_diff)

            # print(
            #     "{} bytes from {} ({})".format(
            #         len(bytearray(recPacket)[20:28]), HOSTNAME, SOURCE_IP_ADDRESS
            #     ), end=": ",)
            # print("icmp_seq={}".format(ICMP_sequence), end=" ")
            # print("ttl={}".format(IP_TTL), end=" ")
            # print("time={0:.3g}ms".format(time_diff))

            if(ICMP_id != ID):
                return "Corrupted"

            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return "Request timed out."
            else:
                return responseMsg

    def sendOnePing(self, mySocket, destAddr, ID):
        # ICMP Header is :
        # type (8), code (8), checksum (16), id (16), sequence (16)
        myChecksum = 0
        # Make a dummy header with a 0 checksum
        # struct -- Interpret strings as packed binary data
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, self.icmp_seq)
        data = struct.pack("d", time.time())
        # Calculate the checksum on the data and the dummy header.
        myChecksum = self.checksum(str(header + data))

        # Get the right checksum, and put in the header
        if sys.platform == "darwin":
            # Convert 16-bit integers from host to network  byte order
            myChecksum = htons(myChecksum) & 0xFFFF
        else:
            myChecksum = htons(myChecksum)

        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, self.icmp_seq)
        packet = header + data
        self.icmp_seq += 1
        # print("1 " ,header ) # Debug use
        # print("2 " ,data) # Debug use
        # print("3 " ,packet ) # Debug use
        mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
        # Both LISTS and TUPLES consist of a number of objects
        # which can be referenced by their position number within the object.

    def doOnePing(self, destAddr, timeout):
        icmp = getprotobyname("icmp")
        # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw

        mySocket = socket(AF_INET, SOCK_RAW, icmp)

        myID = os.getpid() & 0xFFFF  # Return the current process i
        self.sendOnePing(mySocket, destAddr, myID)
        delay = self.receiveOnePing(mySocket, myID, timeout, destAddr)

        mySocket.close()
        return delay

    def ping(self):
        # timeout=1 means: If one second goes by without a reply from the server,
        # the client assumes that either the client's ping or the server's pong is lost
        print("Pinging " + self.target_ip + " using Python:")
        print("")
        # Send ping requests to a server separated by approximately one second
        while 1:
            delay = self.doOnePing(self.target_ip, self.timeout)
            print(delay)
            time.sleep(1)  # one second
        return delay


# ping("google.com")


def main():
    p = ICMPPinger(sys.argv[1], 1)
    p.ping()


if __name__ == "__main__":
    main()
