import npyscreen
import sys
import lib.server as server
import lib.client as client
import time
import curses
import socket
import datetime
from io import StringIO

class chatForm(npyscreen.FormBaseNew):
    def create(self):
        self.chatFeed = self.add(npyscreen.BoxTitle, name="Feed", editable=False, max_height=23)
        self.chatInput = self.add(ChatInput, name="Input", footer="Return -> Send", rely=25)
        self.chatInput.entry_widget.handlers.update({curses.ascii.CR: self.parentApp.sendMessage})
        self.chatInput.entry_widget.handlers.update({curses.KEY_UP: self.parentApp.historyBack})
        self.chatInput.entry_widget.handlers.update({curses.KEY_DOWN: self.parentApp.historyForward})
        
        
class ChatInput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class ChatApp(npyscreen.NPSAppManaged):

    def onStart(self):
        self.chatForm = self.addForm('MAIN', chatForm, name='Peer-2-Peer Chat')
        self.port = 3333
        self.historyLog = []
        self.messageLog = []
        self.partner = ""
        self.nickname = ""
        self.historyPos = 0
        self.hostname = socket.gethostname()
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()
        self.chatClient = client.Client(self)
        self.chatClient.start()

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
            "help": [self.commandHelp, 0, "/help | Shows this help"]
        }

    def restart(self, args=None):
        if self.chatClient.isConnected:
            self.chatClient.send("%/quit")
            self.chatClient.restart()
        if not args == None and args[0] != self.port:
            self.sysMsg("Restarting on port {0}.".format(args[0]))
            self.port = int(args[0])
            self.chatServer.restart()
            time.sleep(1)
            self.chatServer = server.Server(self)
            self.chatServer.daemon = True
            self.chatServer.start()
        else:
            if self.chatServer.hasConnection:
                self.sysMsg("Restarting. Please wait...")
                self.chatServer.restart()
                time.sleep(1)
                self.chatServer = server.Server(self)
                self.chatServer.daemon = True
                self.chatServer.start()
            else:
                self.sysMsg("Restarting.")
            
    def historyBack(self, _input):
        if len(self.historyLog)-1 == 0 or self.historyPos == 0:
            return False
        self.historyPos -= 1
        self.chatForm.chatInput.value = self.historyLog[self.historyPos]


    def historyForward(self, _input):
        if len(self.historyLog)-1 == 0:
            return False
        if self.historyPos == len(self.historyLog)-1:
            self.chatForm.chatInput.value = ""
            return True
        self.historyPos += 1
        self.chatForm.chatInput.value = self.historyLog[self.historyPos]

    def setNickname(self, args):
        self.nickname = args[0]
        self.sysMsg("Set nickname to {0}".format(args[0]))
        if self.chatClient.isConnected:
            self.chatClient.send("%/nick {0}".format(args[0]))

    def sysMsg(self, msg):
        self.messageLog.append("[SYSTEM] "+str(msg))
        if len(self.chatForm.chatFeed.values) > 20:
                self.chatForm.chatFeed.values = []
        self.chatForm.chatFeed.values.append('[SYSTEM] '+str(msg))
        self.chatForm.chatFeed.display()

    def sendMessage(self, _input):
        msg = self.chatForm.chatInput.value
        if msg == "":
            return False
        self.messageLog.append("You > "+msg)
        self.historyLog.append(msg)
        self.historyPos = len(self.historyLog)
        self.chatForm.chatInput.value = ""
        self.chatForm.chatInput.display()
        if len(self.chatForm.chatFeed.values) > 20:
                self.chatForm.chatFeed.values = []
        if msg.startswith('/'):
            self.commandHandler(msg)
        else:
            if self.chatClient.isConnected:
                self.chatClient.send(msg)
                self.chatForm.chatFeed.values.append('You >  {1}'.format(smsg))
                self.chatForm.chatFeed.display()
            else:
                self.sysMsg("You are not connected to a partner. Use /help to find out how to connect.")

    def connectBack(self):
        if self.chatServer.hasConnection and not self.chatClient.isConnected:
            self.chatClient.conn([self.partnerIP, int(self.partnerPort)])
        else:
            self.sysMsg("You are already connected.")

    def logChat(self):
        try:
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            log = open("./logs/p2p-chat-log_{0}.log".format(date), "a")
            for msg in self.messageLog:
                log.write(msg+"\n")
        except Exception:
            self.sysMsg("Could not interact with file.")
            return False
        log.close()
        self.messageLog = []
        self.sysMsg("Dumped log to p2p-chat-log_{0}.log".format(date))
            


    def clearChat(self):
        self.chatForm.chatFeed.values = []
        self.chatForm.chatFeed.display()

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
            

    def exitApp(self):
        if self.chatClient.isConnected:
            self.chatClient.send("%/quit")
        self.chatClient.socket.close()
        self.chatServer.socket.close()
        exit(1)
        

    def commandHandler(self, msg):
        if msg.startswith("/eval"):
            args = msg[6:]
            self.evalCode(args)
            return True

        msg = msg.split(' ')
        command = msg[0][1:]
        args = msg[1:]

        if not command in self.commandDict:
            self.sysMsg("Command not found. Try /help for a list of commands!")
        else:
            if self.commandDict[command][1] == 0:
                self.commandDict[command][0]()
            elif len(args) == self.commandDict[command][1]:
                self.commandDict[command][0](args)
            else:
                self.sysMsg("/{0} takes {1} argument(s) but {2} was/were given.".format(command, self.commandDict[command][1], len(args)))

    def commandHelp(self):
        self.sysMsg("Here's a list of available commands:")
        for command in self.commandDict:
            self.sysMsg(self.commandDict[command][2])

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
    
    chatApp = ChatApp().run()
    