"""
    A simple web server which can only handle http GET request
    It returns a 404 code if the requested file is not available on the server
    Copyright (c) Lin Yunqi 18722016 ,department of Computer and Information Technology, 2020
"""

import socket
import re


def handleRequest(tcpSocket):
    # 1. Receive request message from the client on connection socket
    connectionSocket, addr = tcpSocket.accept()
    message = connectionSocket.recv(1024).decode()
    # 2. Extract the path of the requested object from the message (second part of the HTTP header)
    url = re.split("\s", message, 2)[1][1:]

    try:
        # Read the corresponding file from disk
        f = open(url, mode="r", encoding="utf-8")
    except FileNotFoundError:
        # Send the correct HTTP response error
        errorMessage = "HTTP/1.1 404 Not Found\r\n"
        connectionSocket.send(errorMessage.encode())

    else:
        # Store in temporary buffer
        webPage = f.read()
        f.close()
        statusLine = "HTTP/1.1 200 OK\r\n"
        response = statusLine + "\r\n" + webPage
        # 6. Send the content of the file to the socket
        connectionSocket.send(response.encode())

    # 7. Close the connection socket
    connectionSocket.close()


def startServer(serverAddress, serverPort):
    # 1. Create server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. Bind the server socket to server address and server port
    serverSocket.bind((serverAddress, serverPort))
    # 3. Continuously listen for connections to server socket
    serverSocket.listen(1)
    print("The server is ready to receive")
    # 4. When a connection is accepted, call handleRequest function, passing new connection socket

    while True:
        # The next step is to take care of the HTTP request
        handleRequest(serverSocket)
        #  5. Close server socket


if __name__ == "__main__":
    startServer("", 8000)
