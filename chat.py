import npyscreen
import sys
import lib.server as server
import lib.client as client
import time
import curses
import socket
import datetime
import pyperclip
import os
from io import StringIO

class chatForm(npyscreen.FormBaseNew):
    def create(self):
        self.y, self.x  = self.useable_space()
        self.chatFeed = self.add(npyscreen.BoxTitle, name="Feed", editable=False, max_height=self.y-7)
        self.chatInput = self.add(ChatInput, name="Input", footer="Return -> Send", rely=self.y-5)
        self.chatInput.entry_widget.handlers.update({curses.ascii.CR: self.parentApp.sendMessage})
        self.chatInput.entry_widget.handlers.update({curses.ascii.NL: self.parentApp.sendMessage})
        self.chatInput.entry_widget.handlers.update({curses.KEY_UP: self.parentApp.historyBack})
        self.chatInput.entry_widget.handlers.update({curses.KEY_DOWN: self.parentApp.historyForward})
        self.chatInput.entry_widget.handlers.update({curses.KEY_DOWN: self.parentApp.historyForward})

        new_handlers = {
            "^V": self.parentApp.pasteFromClipboard
        }
        self.add_handlers(new_handlers)
        
        
        
class ChatInput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class ChatApp(npyscreen.NPSAppManaged):
    # Method called at start
    def onStart(self):
        os.system("title P2P-Chat by flowei") # Set window title on windows
        self.chatForm = self.addForm('MAIN', chatForm, name='Peer-2-Peer Chat') # Add chatForm as the main form of npyscreen

        #Get this PCs local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
        except Exception:
            self.sysMsg("It seems like you do not have internet access.")
            self.sysMsg("Could not get host IP. Could not reach Google DNS.")
        self.hostname = s.getsockname()[0]
        s.close()

        #Define initial vars
        self.port = 3333
        self.nickname = ""
        self.partner = ""
        self.partnerIP = "0"
        self.partnerPort = "0"
        self.historyLog = []
        self.messageLog = []
        self.historyPos = 0

        # Start Server and Client threads
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()
        self.chatClient = client.Client(self)
        self.chatClient.start()

        # Dictionary for commands
        self.commandDict = {
            "connect": [self.chatClient.conn, 2, "/connect [host] [port] | Connect to a peer"],
            "disconnect": [self.restart, 0, "/disconnect | Disconnect from the current chat"],
            "nick": [self.setNickname, 1, "/nick [nickname] | Set your nickname"],
            "quit": [self.exitApp, 0, "/quit | Quit the app"],
            "port": [self.restart, 1, "/port [port] | Restart server on specified port"],
            "connectback": [self.connectBack, 0, "/connectback | Connect to the client that is connected to your server"],
            "clear": [self.clearChat, 0, "/clear | Clear the chat. Logs will not be deleted"],
            "eval": [self.evalCode, -1, "/eval | Execute python code"],
            "status": [self.getStatus, 0, "/status | Returns the clients status"],
            "log": [self.logChat, 0, "/log | Logs all messages of the current session to a file."],
            "help": [self.commandHelp, 0, "/help | Shows this help"],
            "flowei": [self.flowei, 0, ""]
        }

        # Dictionary for command aliases
        self.commandAliasDict = {
            "nickname": "nick",
            "conn": "connect",
            "q": "quit",
            "connback": "connectback"
        }

    # Method to reset server and client sockets
    def restart(self, args=None):
        if self.chatClient.isConnected:
            self.chatClient.send("\b/quit")
            time.sleep(0.5)
            self.chatClient.restart()
            self.chatClient = client.Client(self)
            self.chatClient.start()
        if not args == None and args[0] != self.port:
            self.sysMsg("Restarting on port {0}.".format(args[0]))
            self.port = int(args[0])
            self.chatServer.restart()
            time.sleep(0.5)
            self.chatServer = server.Server(self)
            self.chatServer.daemon = True
            self.chatServer.start()
        else:
            self.sysMsg("Restarting connected services...")
            if self.chatServer.hasConnection:
                self.chatServer.restart()
                time.sleep(0.5)
                self.chatServer = server.Server(self)
                self.chatServer.daemon = True
                self.chatServer.start()
                
            
    # Method to scroll back in the history of sent messages
    def historyBack(self, _input):
        if not self.historyLog or self.historyPos == 0:
            return False
        self.historyPos -= 1
        self.chatForm.chatInput.value = self.historyLog[len(self.historyLog)-1-self.historyPos]

    # Method to scroll forward in the history of sent messages
    def historyForward(self, _input):
        if not self.historyLog:
            return False
        if self.historyPos == len(self.historyLog)-1:
            self.chatForm.chatInput.value = ""
            return True
        self.historyPos += 1
        self.chatForm.chatInput.value = self.historyLog[len(self.historyLog)-1-self.historyPos]

    # Method to set nickname of client | Nickname will be sent to peer for identification
    def setNickname(self, args):
        self.nickname = args[0]
        self.sysMsg("Set nickname to {0}".format(args[0]))
        if self.chatClient.isConnected:
            self.chatClient.send("\b/nick {0}".format(args[0]))

    # Method to render system info on chat feed
    def sysMsg(self, msg):
        self.messageLog.append("[SYSTEM] "+str(msg))
        if len(self.chatForm.chatFeed.values) > self.chatForm.y - 10:
                self.clearChat()
        self.chatForm.chatFeed.values.append('[SYSTEM] '+str(msg))
        self.chatForm.chatFeed.display()

    # Method to send a message to a connected peer
    def sendMessage(self, _input):
        msg = self.chatForm.chatInput.value
        if msg == "":
            return False
        if len(self.chatForm.chatFeed.values) > self.chatForm.y - 10:
                self.clearChat()
        self.messageLog.append("You > "+msg)
        self.historyLog.append(msg)
        self.historyPos = len(self.historyLog)
        self.chatForm.chatInput.value = ""
        self.chatForm.chatInput.display()
        if len(self.chatForm.chatFeed.values) > self.chatForm.y - 10:
                self.clearChat()
        if msg.startswith('/'):
            self.commandHandler(msg)
        else:
            if self.chatClient.isConnected:
                self.chatClient.send(msg)
                self.chatForm.chatFeed.values.append('You >  {0}'.format(msg))
                self.chatForm.chatFeed.display()
            else:
                self.sysMsg("You are not connected to a partner. Use /help to find out how to connect.")

    # Method to connect to a peer that connected to the server
    def connectBack(self):
        if self.chatServer.hasConnection and not self.chatClient.isConnected:
            if self.partnerIP == "unknown" or self.partnerPort == "unknown":
                self.sysMsg("Cannot connect. Peer IP and/or port unknown.")
                return False
            self.chatClient.conn([self.partnerIP, int(self.partnerPort)])
        else:
            self.sysMsg("You are already connected.")

    #Method to log the chat to a file | Files can be found in root directory
    def logChat(self):
        try:
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            log = open("p2p-chat-log_{0}.log".format(date), "a")
            for msg in self.messageLog:
                log.write(msg+"\n")
        except Exception:
            self.sysMsg("Could not interact with file.")
            return False
        log.close()
        self.messageLog = []
        self.sysMsg("Dumped log to p2p-chat-log_{0}.log".format(date))
    
    # EASTER EGGGGGGGG
    def flowei(self):
        if os.name == 'nt':
            os.system("start https://flowei.tech")
        else:
            os.system("xdg-open https://flowei.tech")

    #Method to clear the chat feed
    def clearChat(self):
        self.chatForm.chatFeed.values = []
        self.chatForm.chatFeed.display()

    #Method to run python code inside the app | Useful to print app vars
    def evalCode(self, code):
        defaultSTDout = sys.stdout
        redirectedSTDout = sys.stdout = StringIO()
        try:
            exec(code)
        except Exception as e:
            self.sysMsg(e)
        finally:
            sys.stdout = defaultSTDout
        self.chatForm.chatFeed.values.append('> '+redirectedSTDout.getvalue())
        self.chatForm.chatFeed.display()
            
    # Method to exit the app | Exit command will be sent to a connected peer so that they can disconnect their sockets
    def exitApp(self):
        self.sysMsg("Exiting app...")
        if self.chatClient.isConnected:
            self.chatClient.send("\b/quit")
            time.sleep(0.5)
        self.chatClient.restart()
        self.chatServer.restart()
        exit(1)

    # Method to paste text from clipboard to the chat input
    def pasteFromClipboard(self, _input):
        self.chatForm.chatInput.value = pyperclip.paste()
        self.chatForm.chatInput.display()
        
    # Method to handle commands
    def commandHandler(self, msg):
        if msg.startswith("/eval"):
            args = msg[6:]
            self.evalCode(args)
            return True

        msg = msg.split(' ')
        command = msg[0][1:]
        args = msg[1:]
        if command in self.commandAliasDict:
            command = self.commandAliasDict[command]
        if not command in self.commandDict:
            self.sysMsg("Command not found. Try /help for a list of commands!")
        else:
            if self.commandDict[command][1] == 0:
                self.commandDict[command][0]()
            elif len(args) == self.commandDict[command][1]:
                self.commandDict[command][0](args)
            else:
                self.sysMsg("/{0} takes {1} argument(s) but {2} was/were given.".format(command, self.commandDict[command][1], len(args)))

    # Method to print a list of all commands
    def commandHelp(self):
        if len(self.chatForm.chatFeed.values) + len(self.commandDict) + 1 > self.chatForm.y - 10:
            self.clearChat()
        self.sysMsg("Here's a list of available commands:")
        for command in self.commandDict:
            if not self.commandDict[command][2] == "":
                self.sysMsg(self.commandDict[command][2])

    # Method to print the status of server and client
    def getStatus(self):
        self.sysMsg("Client status:")
        if self.chatServer != None:
            serverStatus = True
        else:
            clientStatus = False
        if self.chatClient != None:
            clientStatus = True
        else:
            serverStatus = False
        self.sysMsg("Server > Running: {0} | Port: {1} | Is connected: {2}".format(serverStatus, self.port, self.chatServer.hasConnection))
        self.sysMsg("Client > Running: {0} | Is connected: {1}".format(clientStatus, self.chatClient.isConnected))
        self.sysMsg("Nickname > {0}".format(self.nickname))

if __name__ == '__main__':
    chatApp = ChatApp().run() # Start the app if file is executed
    