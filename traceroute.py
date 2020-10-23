"""
    A pure python traceroute implementation using raw socket.
    Copyright (c) Lin Yunqi 18722016 ,department of Computer and Information Technology, 2020
"""

import select
import struct
import time
import ICMPPing
import socket
import os

ICMP_CODE = socket.getprotobyname("icmp")


def receiveOnePing(icmpSocket, ID, timeSent, timeout):
    while True:
        startedSelect = time.time()
        whatReady = select.select([icmpSocket], [], [], timeout)
        timeInSelect = time.time() - startedSelect

        if whatReady[0] == []:
            return -1
        timeReceived = time.time()

        # attain delay
        delay = (timeReceived - timeSent) * 1000
        delay = int(delay)
        recPack, addr = icmpSocket.recvfrom(1024)
        # Note that if type=11 (Time exceeded), then id and sequence are unused(set to 0)
        type, code, checksum, id, sequence = struct.unpack("bbHHH", recPack[20:28])

        if (type == 11 and code == 0) or (type == 0 and id == ID):
            return (addr[0], delay)

        timeLeft = timeout - timeInSelect
        if timeLeft <= 0:
            return -1


def echo_one(host, ttl):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
    my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    myID = os.getpid() & 0xFFFF
    ICMPPing.sendOnePing(my_socket, host, myID)
    timeSent = time.time()
    ping_res = receiveOnePing(my_socket, myID, timeSent, timeout)
    my_socket.close()
    return ping_res


def echo_three(host, ttl):
    # send three echo request packets
    try1 = echo_one(host, ttl)  # the return value is either (address, delay) or -1
    try2 = echo_one(host, ttl)
    try3 = echo_one(host, ttl)

    ipAddr = "timeout request"

    if try1 == -1:
        try1str = "*"
    else:
        try1str = str(try1[1])
        ipAddr = try1[0]

    if try2 == -1:
        try2str = "*"
    else:
        try2str = str(try2[1])
        ipAddr = try2[0]

    if try3 == -1:
        try3str = "*"
    else:
        try3str = str(try3[1])
        ipAddr = try3[0]

    finalString = \
        '{:>2}  {:>3} ms    {:>3} ms    {:>3} ms    {}'.format(
            str(ttl), try1str, try2str, try3str, ipAddr
        )

    print(finalString)

    if try1 == -1:
        destination_reached = False
    else:
        destination_reached = (try1[0] == socket.gethostbyname(host))

    return destination_reached


def test(ttl):
    host = socket.gethostbyname("lancaster.ac.uk")
    try1 = echo_one(host, ttl)
    if try1 == -1:
        print("fail to receive ping.")
    else:
        print("address: {} time: {} )".format(try1[0], try1[1]))


"""
Main execution starts here
"""
timeout = 2  # Configurable timeout, set using an optional argument
max_tries = 30
host_name = "baidu.com"
ip = socket.gethostbyname(host_name)
print("Traceroute to {} [{}] \n   {} hops max:".format(host_name, ip, max_tries))

for x in range(1, max_tries + 1):
    destination_reached = echo_three(host_name, x)
    if destination_reached:
        break

print("Finished traceroute.")
