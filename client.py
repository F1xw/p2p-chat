import socket
import threading
import sys
import time

class Client(threading.Thread):
    def __init__(self, nick, host, port):
        super(Client, self).__init__()
        self.host = host
        self.port = int(port)
        self.nick = nick

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn()
        print('Verbunden!\n')

    def conn(self):
        self.socket.connect((self.host, self.port))
        self.socket.send(self.nick.encode())
        

    def send(self, msg):
        if msg == '':
            return False
        self.socket.send(msg.encode())


    


