#!/usr/bin/python3

import socket
import sys
import signal
from requests import get

RESP_OK = 'HTTP/1.1 200 OK\n'
CONN_CLOSED = 'Connection: Closed\n'

RESP_NOT_FOUND = "HTTP/1.1 404 Not Found\n"

cachedPages = {}
cachedTypes = {}


def readfile(filename):
    try:
        fo = open('webroot'+filename, 'r+', encoding='utf-8')
        ret = fo.read()
        fo.close()
        ret = ret.encode("utf-8")
        return ret
    except FileNotFoundError:
        pass
    except UnicodeDecodeError:
        pass
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
    if(path == '/'):
        path = '/index.html'

    contype = ''
    body = ''

    # try get from cache
    if(path in cachedPages):
        body = cachedPages[path]
        contype = cachedTypes[path]
        return contype, body

    # read from file
    if(str.endswith(path, 'favicon.ico')):
        contype = 'Content-Type: image/x-icon\n'
        body = readBinaryfile(path)
    elif(str.endswith(path, '.png') or str.endswith(path, '.jpg') or str.endswith(path, '.bmp') or str.endswith(path, '.gif')):
        contype = 'Content-Type: image/png\n'
        body = readBinaryfile(path)
    elif(str.endswith(path, '.css')):
        contype = 'Content-Type: text/css\n'
        body = readfile(path)
    elif(str.endswith(path, '.txt')):
        contype = 'Content-Type: text/plain\n'
        body = readfile(path)
    elif(str.endswith(path, '.html')):
        contype = 'Content-Type: text/html\n'
        body = readfile(path)
    elif(str.endswith(path, '.htm')):
        contype = 'Content-Type: text/html\n'
        body = readfile(path)
    else:
        contype = 'Content-Type: application/octet-stream\n'
        body = readBinaryfile(path)

    if(body == None):
        return None, None

    # cache
    cachedPages[path] = body
    cachedTypes[path] = contype
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
        contype = 'Content-Type: text/plain\n'
        body = "Not Found"
        head = RESP_NOT_FOUND
        head += CONN_CLOSED
        head += contype
        head += 'Content-Length: '+str(len(body))+'\n\n'
        head = head.encode('utf-8')
        clientsocket.send(head)
        clientsocket.send(body.encode("ascii"))


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('0.0.0.0', 8888))
serversocket.listen(10)

print('Running...')

while True:
    clientsocket = None
    try:
        clientsocket, addr = serversocket.accept()
        process_accept(clientsocket)
    except KeyboardInterrupt as ex1:
        print(ex1)
        continue
    except BrokenPipeError as ex2:
        print(ex2)
        continue
    except Exception as ex:
        print(ex)
        continue
    finally:
        if(clientsocket != None):
            try:
                clientsocket.shutdown(2)
                clientsocket.close()
            except Exception as ex99:
                print(ex99)
                pass


serversocket.close()
print("server closed")
