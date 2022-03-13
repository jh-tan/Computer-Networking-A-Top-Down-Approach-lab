from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
ID = os.getpid() & 0xFFFF
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(string):
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


def build_packet():
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 0)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(str(header + data))
    # Get the right checksum, and put in the header
    if sys.platform == "darwin":
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xFFFF
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 0)

    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            icmp = getprotobyname("icmp")

            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack("I", ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = time.time() - startedSelect
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *    Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *    Request timed out.")

            except timeout:
                continue

            else:
                # Fetch the icmp type from the IP packet
                # Refer to the pdf for the location of ICMP types
                bytes = struct.calcsize("b")
                types, = struct.unpack("b", recvPacket[20:20 + bytes])
                try:
                    names = gethostbyaddr(addr[0])[0]
                except herror:
                    names = "Unknown Host"

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    print(
                        "  %d    rtt=%.0f ms    %s ( %s )"
                        % (ttl, (timeReceived - t) * 1000, addr[0],names)
                    )

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    print(
                        "  %d    rtt=%.0f ms    %s ( %s )"
                        % (ttl, (timeReceived - t) * 1000, addr[0],names)
                    )

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    print(
                        "  %d    rtt=%.0f ms    %s ( %s )"
                        % (ttl, (timeReceived - t) * 1000, addr[0],names)
                    )
                    return
                elif types == 8:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]
                    print(
                        "  %d    rtt=%.0f ms    %s ( %s )"
                        % (ttl, (timeReceived - t) * 1000, addr[0],names)
                    )
                    return
                else:
                    print("error")
                break
            finally:
                mySocket.close()

get_route(sys.argv[1])