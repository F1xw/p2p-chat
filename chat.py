import npyscreen
import sys
import lib.server as server
import lib.client as client
from lib.form import ChatForm
from lib.form import ChatInput
import time
import curses
import socket
import datetime
import pyperclip
import os
import json
from io import StringIO

class ChatApp(npyscreen.NPSAppManaged):
    # Method called at start by npyscreen
    def onStart(self):

        # Try to find settings.json file and load its contents.
        # Change language according to settings.json
        # If settings.json is missing, load en.json
        try:
            jsonSettings = open('settings.json')
            self.settings = json.loads(jsonSettings.read())
            jsonSettings.close()
            jsonFile = open('lang/{0}.json'.format(self.settings['language']))
        except Exception:
            jsonFile = open('lang/en.json')
        self.lang = json.loads(jsonFile.read())
        jsonFile.close()

        if os.name == "nt":
            os.system("title P2P-Chat by flowei") # Set window title on windows

        self.ChatForm = self.addForm('MAIN', ChatForm, name='Peer-2-Peer Chat') # Add ChatForm as the main form of npyscreen

        #Get this PCs public IP and catch errors
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            self.hostname = s.getsockname()[0]
            s.close()
        except socket.error as error:
            self.sysMsg(self.lang['noInternetAccess'])
            self.sysMsg(self.lang['failedFetchPublicIP'])
            self.hostname = "0.0.0.0"

        #Define initial variables
        self.port = 3333 # Port the server runs on
        self.nickname = "" # Empty variable to be filled with users nickname
        self.peer = "" # Peer nickname
        self.peerIP = "0" # IP of peer
        self.peerPort = "0" # Port of peer
        self.historyLog = [] # Array for message log
        self.messageLog = [] # Array for chat log
        self.historyPos = 0 # Int for current position in message history

        

        # Start Server and Client threads
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()
        self.chatClient = client.Client(self)
        self.chatClient.start()

        # Dictionary for commands. Includes funtion to call and number of needed arguments
        self.commandDict = {
            "connect": [self.chatClient.conn, 2],
            "disconnect": [self.restart, 0],
            "nickname": [self.setNickname, 1],
            "quit": [self.exitApp, 0],
            "port": [self.restart, 1],
            "connectback": [self.connectBack, 0],
            "clear": [self.clearChat, 0],
            "eval": [self.evalCode, -1],
            "status": [self.getStatus, 0],
            "log": [self.logChat, 0],
            "help": [self.commandHelp, 0],
            "flowei": [self.flowei, 0],
            "lang": [self.changeLang, 1]
        }

        # Dictionary for command aliases
        self.commandAliasDict = {
            "nick": "nickname",
            "conn": "connect",
            "q": "quit",
            "connback": "connectback"
        }

    # Method to change interface language. Files need to be located in lang/
    def changeLang(self, args):
        self.sysMsg(self.lang['changingLang'].format(args[0]))
        try:
            jsonFile = open('lang/{0}.json'.format(args[0]))
            self.lang = json.loads(jsonFile.read())
            jsonFile.close()
        except Exception as e:
            self.sysMsg(self.lang['failedChangingLang'])
            self.sysMsg(e)
            return False
        # Save new settings
        self.settings['language'] = args[0]
        with open('settings.json', 'w') as file:
            file.write(json.dumps(self.settings))

    # Method to reset server and client sockets
    def restart(self, args=None):
        self.sysMsg(self.lang['restarting'])
        if not args == None and args[0] != self.port:
            self.port = int(args[0])
        if self.chatClient.isConnected:
            self.chatClient.send("\b/quit")
            time.sleep(0.2)
        self.chatClient.stop()
        self.chatServer.stop()
        self.chatClient = client.Client(self)
        self.chatClient.start()
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()

                
            
    # Method to scroll back in the history of sent messages
    def historyBack(self, _input):
        if not self.historyLog or self.historyPos == 0:
            return False
        self.historyPos -= 1
        self.ChatForm.chatInput.value = self.historyLog[len(self.historyLog)-1-self.historyPos]

    # Method to scroll forward in the history of sent messages
    def historyForward(self, _input):
        if not self.historyLog:
            return False
        if self.historyPos == len(self.historyLog)-1:
            self.ChatForm.chatInput.value = ""
            return True
        self.historyPos += 1
        self.ChatForm.chatInput.value = self.historyLog[len(self.historyLog)-1-self.historyPos]

    # Method to set nickname of client | Nickname will be sent to peer for identification
    def setNickname(self, args):
        self.nickname = args[0]
        self.sysMsg("{0} {1}".format(self.lang['setNickname'].format(args[0])))
        if self.chatClient.isConnected:
            self.chatClient.send("\b/nick {0}".format(args[0]))

    # Method to render system info on chat feed
    def sysMsg(self, msg):
        self.messageLog.append("[SYSTEM] "+str(msg))
        if len(self.ChatForm.chatFeed.values) > self.ChatForm.y - 10:
                self.clearChat()
        if len(str(msg)) > self.ChatForm.x - 20:
            self.ChatForm.chatFeed.values.append('[SYSTEM] '+str(msg[:self.ChatForm.x-20]))
            self.ChatForm.chatFeed.values.append(str(msg[self.ChatForm.x-20:]))
        else:
            self.ChatForm.chatFeed.values.append('[SYSTEM] '+str(msg))
        self.ChatForm.chatFeed.display()

    # Method to send a message to a connected peer
    def sendMessage(self, _input):
        msg = self.ChatForm.chatInput.value
        if msg == "":
            return False
        if len(self.ChatForm.chatFeed.values) > self.ChatForm.y - 11:
                self.clearChat()
        self.messageLog.append(self.lang['you']+" > "+msg)
        self.historyLog.append(msg)
        self.historyPos = len(self.historyLog)
        self.ChatForm.chatInput.value = ""
        self.ChatForm.chatInput.display()
        if msg.startswith('/'):
            self.commandHandler(msg)
        else:
            if self.chatClient.isConnected:
                if self.chatClient.send(msg):
                    self.ChatForm.chatFeed.values.append(self.lang['you']+" > "+msg)
                    self.ChatForm.chatFeed.display()
            else:
                self.sysMsg(self.lang['notConnected'])

    # Method to connect to a peer that connected to the server
    def connectBack(self):
        if self.chatServer.hasConnection and not self.chatClient.isConnected:
            if self.peerIP == "unknown" or self.peerPort == "unknown":
                self.sysMsg(self.lang['failedConnectPeerUnkown'])
                return False
            self.chatClient.conn([self.peerIP, int(self.peerPort)])
        else:
            self.sysMsg(self.lang['alreadyConnected'])

    #Method to log the chat to a file | Files can be found in root directory
    def logChat(self):
        try:
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            log = open("p2p-chat-log_{0}.log".format(date), "a")
            for msg in self.messageLog:
                log.write(msg+"\n")
        except Exception:
            self.sysMsg(self.lang['failedSaveLog'])
            return False
        log.close()
        self.messageLog = []
        self.sysMsg(self.lang['savedLog'].format(date))
    
    # EASTER EGGGGGGGG
    def flowei(self):
        if os.name == 'nt':
            os.system("start https://flowei.tech")
        else:
            os.system("xdg-open https://flowei.tech")

    #Method to clear the chat feed
    def clearChat(self):
        self.ChatForm.chatFeed.values = []
        self.ChatForm.chatFeed.display()

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
        self.ChatForm.chatFeed.values.append('> '+redirectedSTDout.getvalue())
        self.ChatForm.chatFeed.display()
            
    # Method to exit the app | Exit command will be sent to a connected peer so that they can disconnect their sockets
    def exitApp(self):
        self.sysMsg(self.lang['exitApp'])
        if self.chatClient.isConnected:
            self.chatClient.send("\b/quit")
        self.chatClient.stop()
        self.chatServer.stop()
        exit(1)

    # Method to paste text from clipboard to the chat input
    def pasteFromClipboard(self, _input):
        self.ChatForm.chatInput.value = pyperclip.paste()
        self.ChatForm.chatInput.display()
        
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
            self.sysMsg(self.lang['commandNotFound'])
        else:
            if self.commandDict[command][1] == 0:
                self.commandDict[command][0]()
            elif len(args) == self.commandDict[command][1]:
                self.commandDict[command][0](args)
            else:
                self.sysMsg(self.lang['commandWrongSyntax'].format(command, self.commandDict[command][1], len(args)))

    # Method to print a list of all commands
    def commandHelp(self):
        if len(self.ChatForm.chatFeed.values) + len(self.commandDict) + 1 > self.ChatForm.y - 10:
            self.clearChat()
        self.sysMsg(self.lang['commandList'])
        for command in self.commandDict:
            if not self.lang['commands'][command] == "":
                self.sysMsg(self.lang['commands'][command])

    # Method to print the status of server and client
    def getStatus(self):
        self.sysMsg("STATUS:")
        if self.chatServer: serverStatus = True
        else: serverStatus = False
        if self.chatClient: client = True
        else: clientStatus = False
        self.sysMsg(self.lang['serverStatusMessage'].format(serverStatus, self.port, self.chatServer.hasConnection))
        self.sysMsg(self.lang['clientStatusMessage'].format(clientStatus, self.chatClient.isConnected))
        if not self.nickname == "": self.sysMsg(self.lang['nicknameStatusMessage'].format(self.nickname))

if __name__ == '__main__':
    chatApp = ChatApp().run() # Start the app if chat.py is executed
    