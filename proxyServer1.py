"""
    A simple proxy server which can only handle http GET request
    It supports object caching
    Copyright (c) Lin Yunqi 18722016 ,division of Computer and Information Technology, 2020
"""

from socket import *
import select
import re


def startProxy(serverAddr, port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((serverAddr, port))
    serverSocket.listen(1)
    print("The proxy is ready to receive")

    while True:
        handleRequest(serverSocket)


def handleRequest(serverSocket):
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024).decode()
    #print(message)
    url = re.split("/", message, 3)[2]
    print(url)
    try:
        file = open("webPage.html", "r")
    except:
        file = open("webPage.html", "w")
        file.close()
        file = open("webPage.html", "r")

    # check if the requested file already exists
    content = file.read()
    file.close()
    if re.search(url, content):
        print("The file is already in the proxy")
        statusLine = "HTTP/1.1 200 OK\r\n"
        responseToClient = statusLine + "\r\n" + content
        connectionSocket.send(responseToClient.encode())
        connectionSocket.close()
    else:
        print("Requesting the file from the host...")
        # connect to the host
       # print(url)
        serverName = gethostbyname(url)
       # print(serverName)
        serverPort = 80
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        fullUrl = "http://" + url + "/"
        request = "GET " + fullUrl + " HTTP/1.1\r\n" + "Host: " + url + "\r\n\r\n"
        clientSocket.send(request.encode())

        response=""
        clientSocket.setblocking(0)
        while True:
            ready = select.select([clientSocket], [], [], 2)
            if ready[0]:
                response += clientSocket.recv(4096).decode("gbk", "ignore")
            else:
                break
        clientSocket.close()
        print(response)
        # Download the response html file into disk
        f = open("webPage.html", 'w')
        html = "<html"+re.split("<html", response, 10)[-1] 
        # print(html)
        f.write(html)
        f.close()
        # generate a http response
        statusLine = "HTTP/1.1 200 OK\r\n"
        responseToClient = statusLine + "\r\n" + html

        # Transfer the html file to client
        connectionSocket.send(responseToClient.encode())

        connectionSocket.close()


if __name__ == "__main__":
    startProxy("", 8000)
