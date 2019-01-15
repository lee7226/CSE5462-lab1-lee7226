import select, socket, sys
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
HOST = 'localhost'    # The remote host
#HOST = 'ben-VirtualBox'
PORT = 5001              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

inputs = [s, sys.stdin]

newData = 0


while inputs:
    readable, writable, exceptional = select.select(inputs, inputs, inputs)
    for socket in readable:
        if socket is s:
            data = s.recv(1024)
            if data == "%exit_signal%":
                print ("Exiting...")
                inputs = False
                break;
            print (str(data))
        elif socket is sys.stdin:
            msgToSend = raw_input()
            s.sendall(msgToSend)

s.close()
