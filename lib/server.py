import socket
import threading
import time

class Server(threading.Thread): # Server object is type thread so that it can run simultaniously with the client
    def __init__(self, chatApp): # Initialize with a reference to the Chat App and initial vars
        super(Server, self).__init__()
        self.chatApp = chatApp
        self.port = self.chatApp.port # Get the server port from the Chat App reference
        self.host = "" # Accept all hostnames
        self.hasConnection = False # Connection status
        self.stopSocket = False # Socket interrupt status

        # Information exchange commands used to communicate between peers
        self.commandDict = {
            "nick": [self.setPartnerNickname, 1],
            "quit": [self.partnerQuit, 0],
            "syntaxErr": [self.chatClientVersionsOutOfSync, 0]
        }

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create new socket
        self.socket.bind((self.host, self.port)) # Bind the socket to host and port stored in the servers vars
        self.socket.listen() # Set socket mode to listen

        self.chatApp.sysMsg("Started server on port {0}.".format(self.port))

    # Method to handle information exchange commands
    def commandHandler(self, command):
        command = command.decode().split(" ")
        if len(command) > 1:
            args = command[1:]
        command = command[0][2:]
        if not command in self.commandDict:
            self.chatApp.sysMsg("Your partner sent an invalid command. Make sure they use the same version as you!")
            self.chatApp.chatClient.send("\b/syntaxErr")
        else:
            if self.commandDict[command][1] == 0:
                self.commandDict[command][0]()
            elif len(args) == self.commandDict[command][1]:
                self.commandDict[command][0](args)
            else:
                self.chatApp.sysMsg("Your partner sent an invalid command syntax.")
                self.chatApp.sysMsg("Make sure they use the same version as you!")
                self.chatApp.chatClient.send("\b/syntaxErr")

    # Method called by threading on start
    def run(self):
        conn, addr = self.socket.accept() # Accept a connection
        if self.stopSocket: # Stop the socket if interrupt is set to true
            exit(1)
        init = conn.recv(1024) # Wait for initial information from client
        self.hasConnection = True # Set connection status to true
        
        self.handleInit(init)
        
        while True: # Receive loop
            if len(self.chatForm.chatFeed.values) > self.chatForm.y - 10:
                self.clearChat()
            data = conn.recv(1024) # Wait for data
            if not data: # If data is empty throw an error
                self.chatApp.sysMsg("ERROR: Recieved an empty message.")

            if data.decode().startswith('\b/'): # If data is command for information exchange call the command handler
                self.commandHandler(data)
            else: # Else display the message in chat feed and append it to chat log
                self.chatApp.messageLog.append("{0} >  {1}".format(self.chatApp.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.values.append("{0} >  {1}".format(self.chatApp.partner, data.decode()))
                self.chatApp.chatForm.chatFeed.display()


    def handleInit(self, init):
        if not init: # If initial information is empty, set peer vars to unknown
            self.chatApp.partner = "Unknown"
            self.chatApp.partnerPort = "unknown"
            self.chatApp.partnerIP = 'unknown'
        else: # Decode initial information and set peer vars to values send by peer
            init = init.decode()
            if init.startswith("\b/init"):
                init = init[2:].split(' ')
                self.chatApp.partner = init[1]
                self.chatApp.partnerIP = init[2]
                self.chatApp.partnerPort = init[3]
            else: # If initial information is not sent correctly 
                self.chatApp.partner = "Unknown"
                self.chatApp.partnerPort = "unknown"
                self.chatApp.partnerIP = 'unknown'

        if not self.chatApp.chatClient.isConnected: # Send message to inform about connectBack if client socket is not connected
            if self.chatApp.partnerIP == "unknown" or self.chatApp.partnerPort == "unknown":
                self.chatApp.sysMsg("/connectback is unavailable as peer IP and/or port is unknown.")
            else:
                self.chatApp.sysMsg("A client connected to you. To connect to them type /connectback.")
                self.chatApp.sysMsg("Their IP: {0}, their port: {1}".format(self.chatApp.partnerIP, self.chatApp.partnerPort))

        self.chatApp.sysMsg("{0} joined the chat.".format(self.chatApp.partner)) # Inform user about peer

    # Method called by Chat App to reset server socket
    def restart(self):
        if self.hasConnection:
            self.socket.close()
        else:
            self.stopSocket = True
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', self.port))
            time.sleep(1)
            self.socket.close()
        self.socket = None
        
    # Method called if command for nickname change was received
    def setPartnerNickname(self, nick):
        oldNick = self.chatApp.partner
        self.chatApp.partner = nick[0]
        self.chatApp.sysMsg("{0} changed their name to {1}".format(oldNick, nick[0]))

    # Method called if connected peer quit
    def partnerQuit(self):
        self.chatApp.sysMsg("{0} left the chat.".format(self.chatApp.partner))
        self.chatApp.restart()

    # Method called if connected peer uses an invalid information exchange command syntax
    def chatClientVersionsOutOfSync(self):
        self.chatApp.sysMsg("An error occured while communicating to your partners system. Please make sure that you use the same version as them.")
        