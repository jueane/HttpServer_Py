# coding=utf-8
#!/usr/bin/python3

import socket
import sys
import signal
from requests import get

RESP_OK = "HTTP/1.1 200 OK\n"
CONN_CLOSED = "Connection: Closed\n"
CONTENT_TYPE_HTML = "Content-Type: text/html\n"
CONTENT_TYPE_ICO = "Content-Type: image/x-icon\n"


def readfile(filename):
    try:
        fo = open("webroot/"+filename, "r+", encoding='utf-8')
        ret = fo.read()
        fo.close()
        return ret
    except FileNotFoundError:
        return None


def readBinaryfile(filename):
    try:
        fo = open("webroot/"+filename, "rb")
        ret = fo.read()
        fo.close()
        return ret
    except FileNotFoundError:
        return None


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "0.0.0.0"

port = 8888

serversocket.bind((ip, port))
serversocket.listen(3)

print("Running...")

while True:
    clientsocket, addr = serversocket.accept()

    # recv
    msg = clientsocket.recv(1024)
    req = msg.decode("UTF-8")
    # print(req)

    # req path
    strList = str.split(req, ' ', 2)
    if(len(strList) < 3):
        continue
    path = strList[1]
    print("__req: "+path)
    path = str.replace(path, '/', '', 1)

    if(str.endswith(path, "favicon.ico")):
        head = RESP_OK
        head += CONN_CLOSED
        head += CONTENT_TYPE_ICO
        head += "Content-Length: "

        ico = readBinaryfile(path)
        head += str(len(ico)) + "\n\n"
        clientsocket.send(head.encode("UTF-8"))
        clientsocket.send(ico)
        clientsocket.close()
        continue
    elif(str.endswith(path, ".png") or str.endswith(path, ".jpg") or str.endswith(path, ".bmp") or str.endswith(path, ".gif")):
        head = RESP_OK
        head += CONN_CLOSED
        head += "Content-Type: image/png\n"
        head += "Content-Length: "

        img = readBinaryfile(path)
        head += str(len(img)) + "\n\n"
        clientsocket.send(head.encode("UTF-8"))
        clientsocket.send(img)
        clientsocket.close()
        continue
    elif(str.endswith(path, ".css")):
        head = RESP_OK
        head += CONN_CLOSED
        head += "Content-Type: text/css\n"
        head += "Content-Length: "

        img = readfile(path)
        img = img.encode("UTF-8")
        head += str(len(img)) + "\n\n"
        clientsocket.send(head.encode("UTF-8"))
        clientsocket.send(img)
        clientsocket.close()
        continue
    else:
        if(path == ''):
            path = "index.html"
        # print("client addr: %s" % str(addr))
        head = RESP_OK
        head += CONN_CLOSED
        head += CONTENT_TYPE_HTML
        head += "Content-Length: "

        body = readfile(path)
        if(body == None):
            # resp 404
            clientsocket.close()
            print("not found")
            continue

        body = body.encode("UTF-8")
        lenBody = len(body)
        head += str(lenBody)+"\n\n"

        clientsocket.send(head.encode("UTF-8"))
        clientsocket.send(body)

        clientsocket.close()
