import socket
import threading

HOST = ""
PORT = 3333

class Server(threading.Thread):
    def __init__(self, chatApp):
        super(Server, self).__init__()
        self.chatApp = chatApp
        self.commandDict = {
            "nick": [self.setPartnerNickname, 1],
            "quit": [self.partnerQuit, 0],
            "syntaxErr": [self.chatClientVersionsOutOfSync, 0]
        }

    def commandHandler(self, command):
        command = command.decode().split(" ")
        if len(command) > 1:
            args = command[1:]
        command = command[0][2:]
        if not command in self.commandDict:
            self.chatApp.sysMsg("Your partner sent an invalid command. Make sure they use the same version as you!")
            self.chatApp.chatClient.send("%/syntaxErr")
        else:
            if self.commandDict[command][1] == 0:
                self.commandDict[command][0]()
            elif len(args) == self.commandDict[command][1]:
                self.commandDict[command][0](args)
            else:
                self.chatApp.sysMsg("Your partner sent an invalid command syntax.")
                self.chatApp.sysMsg("Make sure they use the same version as you!")
                self.chatApp.chatClient.send("%/syntaxErr")

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()

        self.chatApp.sysMsg("Started server on port {0}.".format(PORT))

        conn, addr = self.socket.accept()
        init = conn.recv(1024)
        if not init:
            self.chatApp.partner = "Unknown"
        else:
            init = init.decode()
            if init.startswith("%/"):
                command = init[2:].split(' ')
                self.chatApp.partner = command[1]
            else:
                self.chatApp.partner = "Unknown"

        self.chatApp.sysMsg("{0} joined the chat.".format(self.chatApp.partner))
        
        while True:
            if len(self.chatApp.chatForm.chatFeed.values) > 20:
                self.chatApp.chatForm.chatFeed.values = []

            data = conn.recv(1024)
            if not data:
                self.chatApp.sysMsg("ERROR: Recieved an empty message.")

            if data.decode().startswith('%/'):
                self.commandHandler(data)
            else:
                self.chatApp.chatForm.chatFeed.values.append("{0}>  {1}".format(self.chatApp.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.display()

    def disconn(self):
        self.socket.close()
        self.socket = None
        self.run()

    def setPartnerNickname(self, nick):
        oldNick = self.chatApp.partner
        self.chatApp.partner = nick[0]
        self.chatApp.sysMsg("{0} changed their name to {1}".format(oldNick, nick[0]))

    def partnerQuit(self):
        self.chatApp.sysMsg("{0} left the chat. Disconnecting services...".format(self.chatApp.partner))
        self.chatApp.disconn()

    def chatClientVersionsOutOfSync(self):
        self.chatApp.sysMsg("An error occured while communicating to your partners system. Please make sure that you use the same version as them.")
        