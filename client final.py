import socket
import select
import sys
import time
from threading import Thread

user = ""
def prompt(user):
    line = "> " 
    if len(user) > 0:
        line = "@" + user + ": "
    sys.stdout.write("\033[35m")
    sys.stdout.write(line)
    sys.stdout.flush()
    sys.stdout.write('\033[0m')

def friend_prompt(friend):
    line = "> " 
    if len(friend) > 0:
        line = "@" + friend + ": "
    sys.stdout.write('\33[33m')
    sys.stdout.write(line)
    sys.stdout.flush()

def server_prompt():
    sys.stdout.write("server: ")
    sys.stdout.write("\033[35m")
    sys.stdout.flush()
    sys.stdout.write('\033[0m')

class Client(object):
    sys.stdout.write('\033[0m')

    def __init__(self):
        self.host = "18.195.107.195"
        self.port = 5378
        self.sock = None
        self.connect_to_server()

    def false_username(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        
        try:
            self.sock.connect((self.host, self.port))
        except:
            sys.stdout.write("\033[31m")
            print ('Unable to connect')
            sys.stdout.write('\033[0m')
            sys.exit()

        sys.stdout.write("\033[32m")
        print ('This username is taken.')
        print ('Type in other username.')
        sys.stdout.write('\033[0m')
        prompt(user)

        self.wait_for_messages()

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        
        try:
            self.sock.connect((self.host, self.port))
        except:
            sys.stdout.write("\033[31m")
            print ('Unable to connect')
            sys.stdout.write('\033[0m')
            sys.exit()

        sys.stdout.write("\033[32m")
        print ('Connected.')
        print ('Type in your username.')
        sys.stdout.write('\033[0m')
        prompt(user)

        self.wait_for_messages()

    def wait_for_messages(self):
        check = True
        while 1:
            socket_list = [sys.stdin, self.sock]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                if sock == self.sock:
                    data = sock.recv(4096)

                    if not data:
                        self.false_username()
                    elif data == "SEND-OK\n":
                        data = "Message was successfully sent\n"
                        sys.stdout.write(data)
                    elif data.find("DELIVERY") == 0:
                        message = data[data.index("DELIVERY")+9:len(data)]
                        friend = message[0:message.index(" ")]
                        friend_message = message[message.index(" ")+1:len(message)]
                        data = friend_message
                        friend_prompt(friend)
                        sys.stdout.write(data)
                        sys.stdout.write('\033[0m')
                        prompt(user)
                    elif data == "BAD-RQST-HDR\n":
                        data = "Incorrect input - your message contains an error in the header.\n"
                        sys.stdout.write(data)
                        prompt(user)
                    elif data == "BAD-RQST-BODY\n":
                        data = "Incorrect input - your message contains an error in the body.\n"
                        sys.stdout.write(data)
                        prompt(user)
                    else:
                        sys.stdout.write(data)
                        prompt(user)
                else:
                    msg = sys.stdin.readline()
                    new_msg = msg[:-1]

                    if msg == "!quit\n":
                        sys.stdout.write("\033[31m")
                        print ('Disconnected from chat server by typing "quit"')
                        sys.stdout.write('\033[0m')
                        sys.exit()
                    else:
                        if check:
                            self.sock.send(("HELLO-FROM " + msg).encode())
                            user = new_msg
                            check = False
                        else: 
                            if msg[0] == "@" and msg.count(" ") > 0:
                                send_to =  msg[1:msg.index(" ")]
                                send_message = msg[msg.index(" "):len(msg)]
                                message = "SEND " + send_to + send_message
                                self.sock.send((message).encode())
                            elif msg == "!who\n":
                                self.sock.send(("WHO\n").encode())
                            else:
                                msg = msg.encode()
                                self.sock.sendall(msg)                         
                        server_prompt()

if __name__ == '__main__':
    client = Client()