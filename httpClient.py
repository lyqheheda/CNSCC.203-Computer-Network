"""
    A simple http client which can only generate http GET request, as the additional assignment of task 2.1
    Copyright (c) Lin Yunqi 18722016 ,department of Computer and Information Technology, 2020
"""

from socket import *
import re

def startClient(url):
    # parse the url
    slice=re.split("/",url,1)
    ipAndPort=slice[0]
    subURL=slice[1]
    subSlice=re.split(":",ipAndPort,1)
    ipAddr=subSlice[0]
    port=int(subSlice[1])

    # connect to the server
    clientSocket=socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((ipAddr,port))
    # generate http GET request
    request = "GET /" + subURL + " HTTP/1.1\r\n" + "Host: " + ipAndPort + "\r\n\r\n"
    clientSocket.send(request.encode())
    # receive the http response
    response=""
    while(not re.search("</html>$",response)):
        response += clientSocket.recv(1024).decode("gbk", "ignore")



    # Download the response html file into disk

    f = open("httpClientWebpage.html", 'w')
    html = re.split("\r\n", response, 100)[-1]

    f.write(html)
    f.close()
    print("The requested file has been downloaded")

    clientSocket.close()

if __name__=="__main__":
    startClient("127.0.0.1:8000/index.html" )