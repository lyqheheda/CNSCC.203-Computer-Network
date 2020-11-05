"""
    A simple proxy server which can only handle http GET request
    It supports object caching
    Copyright (c) Lin Yunqi 18722016 ,division of Computer and Information Technology, 2020
"""

from socket import *
import re
import sys


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
    url = re.split("/", message, 3)[2]
    #print(url)

    # check if the requested file already exists
    try:
        file=open("webPage.html","r")
    except:

        pass
    else:
        content=file.read()
        if re.search(url,content):



    # if :
    #     #The webpage is cached
    #     pass
    # else:
    # send http request to the specified host
    serverName = url
    serverPort = 80
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    fullUrl="http://"+url+"/"
    request="GET "+fullUrl+" HTTP/1.1\r\n"+"Host: "+url+"\r\n\r\n"

    clientSocket.send(request.encode())
    response=clientSocket.recv(1024).decode()

    # Download the response html file into disk
    f = open("webPage.html", 'w')
    html=re.split("\r\n",response,100)[-1]
    #print(html)
    f.write(html)
    f.close()
    # generate a http response
    statusLine = "HTTP/1.1 200 OK\r\n"
    responseToClient=statusLine + "\r\n" +html

    # Transfer the html file to client
    connectionSocket.send(responseToClient.encode())

    connectionSocket.close()


if __name__ == "__main__":
    startProxy("", 8000)
