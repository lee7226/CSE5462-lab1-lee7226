import select, socket, sys
import os

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue
# Echo client program
import socket
import time

# Author: Ben Lee

count = 0
HOST = 'localhost'       # The remote host defaults to localhost, actual host is entered by user
PORT = 5001              # The same port as used by the server

HOST = raw_input('Enter IP address of server: ')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


inputs = [s, sys.stdin]

newData = 0

# open connection, send fileName to host, close connection
def sendFile(fileName, host):
    try:
        send_sock = socket.socket()
        send_sock.connect((host,5002))
        f = open (fileName, "rb")
        data = f.read(1024)
        while (data):
            send_sock.send(data)
            data = f.read(1024)
    finally:
        send_sock.close()

# open connection, write data from host to fileName, close connection
def receiveFile(fileName, host):
    try:
        recv_sock = socket.socket()
        recv_sock.bind((host,5002))
        recv_sock.listen(5)
        connection, address = recv_sock.accept()

        f = open(fileName,'wb')
        fileDone = False
        while not (fileDone):
            data = connection.recv(1024)
            while (data):
                f.write(data)
                data = connection.recv(1024)
            fileDone = True
    finally:
        f.close()

        connection.close()
        recv_sock.close()


while inputs:
    readable, writable, exceptional = select.select(inputs, inputs, inputs)
    for sock in readable:
        if sock is s:
            data = s.recv(1024)
            # end the program
            if data == "%exit_signal%":
                print ("Exiting...")
                inputs = False
                break;

            # receive requested file from peer
            if data.startswith('FileRequest:'):
                print('Downloading file...')
                words = data.split(':')
                try:
                    receiveFile(words[1], words[2])
                    print('Success')
                except:
                    print('Failed to Download file')
            # send requested file to peer
            elif data.startswith('SendFile:'):
                words = data.split(':')
                try:
                    sendFile(words[1], words[2])
                except:
                    a = 0
            # else print out received data
            else:
                print (str(data))
        elif sock is sys.stdin:
            msgToSend = raw_input()
            s.sendall(msgToSend)
            
            # if client is logging in or creating account, send file and connection data to server
            if msgToSend.startswith('login') or msgToSend.startswith('register'):
                filesStr = 'SharedFilesIdentifier: '
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                for f in files:
                    filesStr += f + ','
                filesStr = filesStr[:-1]
                filesStr += ' ' + socket.gethostbyname(socket.gethostname())
                s.sendall(filesStr)

s.close()