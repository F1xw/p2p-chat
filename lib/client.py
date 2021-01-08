import socket
import threading
import sys
import time

class Client(threading.Thread):
    def __init__(self, chatApp):
        super(Client, self).__init__()
        self.chatApp = chatApp
        self.isConnected = False

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

    def conn(self, args):
        if self.chatApp.nickname == "":
            self.chatApp.sysMsg("You nickname is not set. Try /help to find out how.")
            return False
        host = args[0]
        port = int(args[1])
        self.chatApp.sysMsg("Connecting to {0} on port {1}".format(host, port))
        try:
            self.socket.connect((host, port))
        except socket.error:
            self.chatApp.sysMsg("Could not connect. Attempt timed out.")
            return False
        self.socket.send("%/init {0} {1} {2}".format(self.chatApp.nickname, "localhost", self.chatApp.port).encode())
        self.chatApp.sysMsg("Connected.")
        self.isConnected = True
    
    def restart(self):
        self.socket.shutdown(1)
        socket.SH
        self.isConnected = False

    def send(self, msg):
        if msg != '':
            self.socket.send(msg.encode())


    


