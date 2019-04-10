#!/usr/bin/python3

import socket
import sys
import signal
from requests import get

RESP_OK = 'HTTP/1.1 200 OK\n'
CONN_CLOSED = 'Connection: Closed\n'
ip = '0.0.0.0'
port = 8888


def readfile(filename):
    try:
        fo = open('webroot'+filename, 'r+', encoding='utf-8')
        ret = fo.read()
        fo.close()
        ret = ret.encode("utf-8")
        return ret
    except FileNotFoundError:
        return None


def readBinaryfile(filename):
    try:
        fo = open('webroot'+filename, 'rb')
        ret = fo.read()
        fo.close()
        return ret
    except FileNotFoundError:
        return None


def process_body(path):
    contype = ''
    body = ''

    if(str.endswith(path, 'favicon.ico')):
        contype = 'Content-Type: image/x-icon\n'
        body = readBinaryfile(path)
    elif(str.endswith(path, '.png') or str.endswith(path, '.jpg') or str.endswith(path, '.bmp') or str.endswith(path, '.gif')):
        contype = 'Content-Type: image/png\n'
        body = readBinaryfile(path)
    elif(str.endswith(path, '.css')):
        contype = 'Content-Type: text/css\n'
        body = readfile(path)
    else:
        if(path == '/'):
            path = '/index.html'
        contype = 'Content-Type: text/html\n'
        body = readfile(path)
    return contype, body


def process_accept(clientsocket):
    # recv
    msg = clientsocket.recv(1024)
    req = msg.decode('utf-8')

    # req path
    strList = str.split(req, ' ', 2)
    if(len(strList) < 3):
        return
    path = strList[1]
    print('__req: '+path)

    contype, body = process_body(path)

    # resp
    if(body != None):
        head = RESP_OK
        head += CONN_CLOSED
        head += contype
        head += 'Content-Length: '+str(len(body))+'\n\n'
        head = head.encode('utf-8')
        clientsocket.send(head)
        clientsocket.send(body)
    else:
        # resp 404
        print('not found')

    clientsocket.close()


serversocket = None
clientsocket = None

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((ip, port))
serversocket.listen(10)

print('Running...')

try:
    while True:
        clientsocket, addr = serversocket.accept()
        process_accept(clientsocket)
except KeyboardInterrupt as identifier:
    pass
finally:
    serversocket.close()
    if(clientsocket != None):
        clientsocket.shutdown(2)
        clientsocket.close()
    print("server closed")
