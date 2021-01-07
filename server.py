import socket
import threading

HOST = ""
PORT = 3333

class Server(threading.Thread):
    def __init__(self, chatApp):
        super(Server, self).__init__()
        self.chatApp = chatApp

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        print("Server running on port {0}".format(PORT))
        self.chatApp.chatForm.chatFeed.values.append("[SYSTEM] Server wurde auf Port {0} gestartet.".format(PORT))
        conn, addr = self.socket.accept()
        nick = conn.recv(1024)
        if not nick:
            self.partner = "Unknown"
        else:
            self.partner = str(nick.decode())
        print("\n{0} ist beigetreten".format(self.partner))
        self.chatApp.chatForm.chatFeed.values.append("[SYSTEM] {0} ist beigetreten.".format(self.partner))
        self.chatApp.chatForm.chatFeed.display()
        while True:
            if len(self.chatApp.chatForm.chatFeed.values) > 20:
                self.chatApp.chatForm.chatFeed.values = []
            data = conn.recv(1024)
            if not data:
                print("\nERROR: Empty message recieved")
            if data.decode() == "/test":
                continue
            if data.decode() == "/quit":
                print("[SYSTEM] {0} hat die Verbindung getrennt!\n Beende den Chat...".format(self.partner))
                self.chatApp.chatForm.chatFeed.values.append("{0} hat die Verbindung getrennt!\n Zum beenden drücke STRG + Q.".format(self.partner))
                self.chatApp.chatForm.chatFeed.display()
                while True:
                    pass
            else:
                print('\n{0}: {1}'.format(self.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.values.append("{0}>  {1}".format(self.partner, data.decode()))
            self.chatApp.chatForm.chatFeed.display()

