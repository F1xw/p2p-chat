import socket
import threading
import time

class Server(threading.Thread):
    def __init__(self, chatApp):
        super(Server, self).__init__()
        self.chatApp = chatApp
        self.port = self.chatApp.port
        self.host = ""
        self.hasConnection = False
        self.stopSocket = False
        self.commandDict = {
            "nick": [self.setPartnerNickname, 1],
            "quit": [self.partnerQuit, 0],
            "syntaxErr": [self.chatClientVersionsOutOfSync, 0]
        }
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

        self.chatApp.sysMsg("Started server on port {0}.".format(self.port))


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
        conn, addr = self.socket.accept()
        if self.stopSocket:
            exit(1)
        init = conn.recv(1024)
        self.hasConnection = True
        
        if not init:
            self.chatApp.partner = "Unknown"
        else:
            init = init.decode()
            if init.startswith("%/init"):
                init = init[2:].split(' ')
                self.chatApp.partner = init[1]
                self.chatApp.partnerPort = init[3]
                self.chatApp.partnerIP = socket.gethostbyname(init[2])
            else:
                self.chatApp.partner = "Unknown"
                self.chatApp.partnerPort = "unknown"
                self.chatApp.partnerIP = 'unknown'

        if not self.chatApp.chatClient.isConnected:
           self.chatApp.sysMsg("A client connected to you. To connect to them type /connectback.")
           self.chatApp.sysMsg("Their IP: {0}, their port: {1}".format(self.chatApp.partnerIP, self.chatApp.partnerPort))

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
                self.chatApp.messageLog.append("{0} >  {1}".format(self.chatApp.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.values.append("{0} >  {1}".format(self.chatApp.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.display()


    def restart(self):
        if self.hasConnection:
            self.socket.close()
        else:
            self.stopSocket = True
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', self.port))
            time.sleep(1)
            self.socket.close()
        self.socket = None
        

    def setPartnerNickname(self, nick):
        oldNick = self.chatApp.partner
        self.chatApp.partner = nick[0]
        self.chatApp.sysMsg("{0} changed their name to {1}".format(oldNick, nick[0]))

    def partnerQuit(self):
        self.chatApp.sysMsg("{0} left the chat.".format(self.chatApp.partner))
        self.chatApp.restart()

    def chatClientVersionsOutOfSync(self):
        self.chatApp.sysMsg("An error occured while communicating to your partners system. Please make sure that you use the same version as them.")
        