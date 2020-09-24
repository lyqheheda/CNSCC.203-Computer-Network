#!/usr/bin/python


import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    if sys.platform == 'darwin':
        answer = socket.htons(answer) & 0xffff
    else:
        answer = socket.htons(answer)

    return answer


def receiveOnePing(icmpSocket, ID, timeout):
    # 1. Wait for the socket to receive a reply
    while True:
        startedSelect = time.time()
        whatReady = select.select([icmpSocket], [], [], timeout)
        timeInSelect = time.time() - startedSelect

        # 2. Once received, record time of receipt, otherwise, handle a timeout
        if whatReady[0] == []:
            return -1
        timeReceived = time.time()
        recPack, addr = icmpSocket.recvfrom(1024)
        type, code, checksum, id, sequence = struct.unpack("bbHHH", recPack[20:28])
        # 3. Check that the ID matches between the request and reply
        if type == 0 and id == ID:
            bytesInDouble = struct.calcsize("d")
            # 4. Unpack the packet header for useful information, including the ID
            timeSent = struct.unpack("d", recPack[28:28 + bytesInDouble])[0]
            # 5. Compare the time of receipt to time of sending, producing the total network delay
            delay = timeReceived - timeSent
            # 6. Return total network delay
            return delay

        timeLeft = timeout - timeInSelect
        if timeLeft <= 0:
            return -1


def sendOnePing(icmpSocket, destinationAddress, ID):
    """
    Send one ping to destinationAddress
    """
    # 1. Build ICMP header
    destinationAddress = socket.gethostbyname(destinationAddress)

    # ICMP header format: type(8), code(8), checksum(16), id(16), sequence(16)
    my_checksum = 0

    # Make a dummy header with a 0 checksum.
    header = struct.pack("bbHHH",  # different with sample code bbHHh
                         ICMP_ECHO_REQUEST, 0, my_checksum, ID,
                         1)  # didn't use socket.htons(my_checksum). Does it matter?
    bytesInDouble = struct.calcsize("d")
    paddingData = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + paddingData.encode()
    packet = header + data

    # 2. Checksum ICMP packet using given function
    my_checksum = checksum(packet) #&0xFFFF

    # 3. Insert checksum into packet
    header = struct.pack("bbHHH", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    packet = header + data

    # 4. Send packet using socket
    icmpSocket.sendto(packet, (destinationAddress, 80))  # 80 is the port?


def doOnePing(destinationAddress, timeout):
    # 1. Create ICMP socket
    icmp = socket.getprotobyname('icmp')
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    # 2. Call sendOnePing function
    myID = os.getpid() & 0xFFFF
    sendOnePing(mySocket,destinationAddress,myID)
    # 3. Call receiveOnePing function
    delay=receiveOnePing(mySocket,myID,timeout)
    # 4. Close ICMP socket
    mySocket.close()
    # 5. Return total network delay
    return delay



def ping(host, timeout=1):
    # 1. Look up hostname, resolving it to an IP address
    for i in range(4):
        print("ping {}...".format(host))
    # 2. Call doOnePing function, approximately every second
        try:
            delay=doOnePing(host,timeout)
        except socket.gaierror as e:
            print(e)
            break
        if delay==-1:
            print('failed. Timeout within {} seconds.'.format(timeout))
        else:
            delay=delay*1000
            print('get ping in %.4fms'% delay)
    print()
    # 3. Print out the returned delay
    # 4. Continue this process until stopped



ping("lancaster.ac.uk")
