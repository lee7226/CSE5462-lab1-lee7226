import select, socket, sys
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue
import csv
import os

# Author: Ben Lee

user_name = []
socket_list = []
online_list = []
connections = 0
user_connection = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((socket.gethostbyname(socket.gethostname()), 5001))
print('server bound to: ' + socket.gethostbyname(socket.gethostname()))
server.listen(5)
inputs = [server, sys.stdin]
newData = 0
ipMap = {}

# the file to store users
userFileName = 'userTable.csv'

# create an empty file if one does not exist
if not os.path.exists(userFileName):
    file(userFileName, "w").close()

#open and read the files, placing the data in a 2d array of [username, password]
userTableFile = open(userFileName, "r+");

reader = csv.reader(userTableFile)
userTable = [[str(s) for s in r] for r in reader]
fileTable = []

while inputs:
    
    readable, writable, exceptional = select.select(
        inputs, inputs, inputs)
    for s in readable:
        # this stanza handles connection requests. 
        if s is server:
            print ("received a connect requst from a client ")
            print
            connection, client_address = s.accept()
            if connections == 0:
                connections = 1
                connection1 = connection
            else:
                connection2 = connection
            print ("connection is {}".format (connection))
            connection.setblocking(0)
            connection.send("Welcome! Type \"help\" for a list of commands")
            inputs.append(connection)
        elif s is sys.stdin:
            newData = 1;
            command_string = raw_input()
            print ("received:::: " + command_string)
        else:
            # this stanza handles already connected sockets (data from clients)
            data = s.recv(1024)
            if data:

                # if this is the first time i've seen this socket
                # i want to add it to an array called 'outputs',
                # i use outputs to allow me to queue data to send
#                s.send ("echo response => " + data)
                print ("read " + data)
                words = data.split()
                print ("received '" + data + "'")
                for i,word in enumerate(words):
                    # register new users if there is no existing user with the same username
                    if word == "register":
                        send_sock = s
                        if not s in user_connection.values():
                            userID = words[i+1]
                            password = words[i+2]
                            user = [userID, password]
                            newUser = True
                            for existingUser in userTable:
                                if existingUser[0] == userID:
                                    newUser = False
                                    break
                            if not newUser:
                                send_sock.send("Username already exists")
                            else:
                                user_connection[userID] = s
                                userTable.append(user)
                                csv.writer(userTableFile).writerow(user)
                                send_sock.send("Welcome " + userID + "!")
                        else:
                            send_sock.send("You're already logged in")
                    # login client
                    elif word == "login":
                        userID = words[i+1]
                        password = words[i+2]
                        print ("userid {} and password {} ".format(userID, password))	
                        send_sock = s
                        # make sure entered password matches table password
                        if not s in user_connection.values():
                            if not [userID, password] in userTable:
                                send_sock.send("Username or password is incorrect")
                            else:
                                # don't let user log in if that user is already logged in
                                if not userID in user_connection.keys():
                                    user_connection[userID] = s
                                    send_sock.send("Welcome back " + userID + "!")
                                else:
                                    send_sock.send("User is already logged in")
                        # can't log in multiple times from same client
                        else:
                            send_sock.send("already logged in as another user")
                    # remove user from user dictionary
                    elif len(words) == 1 and (word == "logout" or word == "exit"):
                        userID = user_connection.keys()[user_connection.values().index(s)]
                        for f in fileTable:
                        	if f[0] == userID:
                        		del fileTable[fileTable.index(f)]
                        user_connection = {k: v for k,v in user_connection.items() if v != s}
                        # send an exit signal to kill the client process 
                        if word == "exit":
                            send_sock = s
                            # send some predetermined signal to help avoid any accidental exit signals being sent
                            send_sock.send("%exit_signal%")

                    # logic for actually sending messages
                    elif word == "msg":
                        # can only send messages if client is logged in
                        if not s in user_connection.values():
                            send_sock = s
                            send_sock.send("You are not logged in")
                        else:
                            userID = words[i+1]
                            msg = ""
                            # build the message that is being sent
                            for j in range(i+2, len(words)):
                                msg += words[j]
                                if j < len(words)-1:
                                    msg += " "
                            # only send a message if the destination user is online 
                            if userID in user_connection.keys():
                                sender_name = user_connection.keys()[user_connection.values().index(s)]
                                # send the message along with a tag saying who it is from
                                if not userID == sender_name:
                                    send_sock = user_connection[userID]
                                    send_sock.send("From " + sender_name + ": " + msg)
                                # no need to send messages to yourself, unless you are very lonely and/or there's nobody else online 
                                # (which considering that this is currently only a local application this is a disctinct possibility)
                                else:
                                    send_sock = s
                                    send_sock.send("Quit talking to yourself")
                            else:
                                send_sock = s
                                send_sock.send("User is not online")
                    # display a list of users that are currently online
                    elif word == "list" and len(words) == 1:
                        user_list = "Online users:\n"
                        index = 0
                        for i in user_connection:
                            user_list += i
                            if index < len(user_connection) - 1:
                                user_list += "\n"
                            index += 1
                        send_sock = s
                        send_sock.send(user_list)
                    # receive file and connection data when a user logs in
                    elif word == 'SharedFilesIdentifier:':
                        print('received files to be read')
                        print(words[1])
                        if s in user_connection.values():
                            userID = user_connection.keys()[user_connection.values().index(s)]
                            userFileList = [userID, words[1]]
                            fileTable.append(userFileList)
                            ipMap[userID] = words[2]
                    # send client a list of files that are available for file sharing, not including the client's own files and not including duplicates
                    elif word == 'files':
                        if not s in user_connection.values():
                            s.send('You are not logged in')
                        else:
                            allFiles = ''
                            userID = user_connection.keys()[user_connection.values().index(s)]
                            userFiles = []
                            for r in fileTable:
                                if r[0] in user_connection.keys() and r[0] is not userID:
                                    allFiles += r[1]
                                if r[0] is userID:
                                	userFiles = r[1].split(',')
                                allFiles += ','
                            s.send('available files:\n')
                            allFileList = allFiles.split(',')
                            allFileList = list(set(allFileList) - set(userFiles))
                            msgToSend = '';
                            for f in allFileList:
                            	if (len(f) > 0):
                        			msgToSend += f + '\n'
                            s.send(msgToSend)
                    # send data to both the client requesting a file and the first client who owns that file so that each client can receive/send the file
                    elif word == 'download':
                        if not s in user_connection.values():
                            s.send('You are not logged in')
                        else:
                            if len(words) > 1:
                                fileToDownload = words[1]
                                foundFile = False
                                for r in fileTable:
                                    filesArr = r[1].split(',')
                                    if fileToDownload in filesArr:
                                        foundFile = True
                                        userID = user_connection.keys()[user_connection.values().index(s)]
                                        senderIP = ipMap[r[0]]
                                        receiverIP = ipMap[userID]
                                        print('fileToDownload = ' + fileToDownload)
                                        print('senderIP = ' + senderIP)
                                        print('receiverIP = ' + receiverIP)
                                        print('sending file')
                                        s.send('FileRequest:' + fileToDownload + ':' + receiverIP)
                                        fileOwnerSocket = user_connection.get(r[0])
                                        fileOwnerSocket.send('SendFile:' + fileToDownload + ':' + senderIP)
                                        break
                                if not foundFile:
                                    s.send('file does not exist')
                    # send client a list of all the users who own the requested file
                    elif word == 'location':
                        if not s in user_connection.values():
                            s.send('You are not logged in')
                        else:
                            if len(words) > 1:
                                fileToLocate = words[1]
                                foundFile = False
                                sendStr = 'file: \"' + fileToLocate + '\" belongs to:\n'
                                for r in fileTable:
                                    filesArr = r[1].split(',')
                                    if fileToLocate in filesArr:
                                        sendStr +=  r[0] + '\n'
                                        foundFile = True
                                if not foundFile:
                                    s.send('file: \"' + fileToLocate + '\" cannot be located')
                                else:
                                    s.send(sendStr)
                    # display a list of commands
                    elif word == "help" and len(words) == 1:
                        commands = "Commands:\n"
                        commands += "register <username> <password>\n\t- Register new user\n"
                        commands += "Login <username> <password>\n\t- Login to account\n"
                        commands += "list\n\t- List all online users\n"
                        commands += "msg <username> <message>\n\t- Sends <message> to <username>\n"
                        commands += "logout\n\t- Logs out of current user\n"
                        commands += "exit\n\t- Exits the client\n"
                        commands += "files\n\t- List the files available to download from other clients\n"
                        commands += "location <filename>\n\t- List the user(s) who owns the specified file\n"
                        commands += "download <filename>\n\t- Download the specified file from a user who owns it\n"
                        commands += "help\n\t- List commands\n"
                        send_sock = s
                        send_sock.send(commands)
                if newData == 1:
                    data = command_string
                    newData = 0

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

# save and close the usertable
writer = csv.writer(userTableFile)
[writer.writerow(r) for r in userTable]
userTableFile.close()
