import sys
import os
import time
import socket
import threading

HOST = ""
PORT = 3333

class Server(threading.Thread):
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        print("Server running on port {0}".format(PORT))
        conn, addr = self.socket.accept()
        nick = conn.recv(1024)
        if not nick:
            self.partner = "Unknown"
        else:
            self.partner = str(nick.decode())
        print("\n{0} connected".format(self.partner))
        while True:
            data = conn.recv(1024)
            if not data:
                print("\nERROR: Empty message recieved")
            if data.decode() == "/quit":
                print("{0} hat die Verbindung getrennt!\n Beende den Chat...")
                os._exit(1)
            print('\n{0}: {1}'.format(self.partner, data.decode()))

