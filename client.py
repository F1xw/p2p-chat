import socket
import threading
import sys
import time

class Client(threading.Thread):
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = input('IP des Chatpartners:')
        self.port = int(input('Port des Chatpartners:'))
        self.nick = input('Wie willst du heißen?')

        self.conn()
        print('Verbunden!\n')

        while True:
            msg = input('>')
            if msg == '':
                continue
            if msg == '/quit':
                self.send("/quit")
                exit()
            self.send(msg)

    def conn(self):
        self.socket.connect((self.host, self.port))
        self.socket.send(self.nick.encode())
        

    def send(self, msg):
        self.socket.send(msg.encode())


    


