import npyscreen
import server
import client
import time
import curses

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
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()
        self.chatClient = client.Client(self)
        self.chatClient.start()
        self.historyLog = []
        self.partner = ""
        self.nickname = ""
        self.historyPos = 0

        self.commandDict = {
            "connect": [self.chatClient.conn, 2, "/connect [host] [port] | Connect to a peer"],
            "disconnect": [self.disconn, 0, "/disconnect | Disconnect from the current chat"],
            "nick": [self.setNickname, 1, "/nick [nickname] | Set your nickname"],
            "quit": [self.exitApp, 0, "/quit | Quit the app"],
            "help": [self.commandHelp, 0, "/help | Shows this help"]
        }

    def disconn(self):
        self.chatClient.send("%/quit")
        self.chatClient.disconn()
        self.chatServer.disconn()
        self.sysMsg("Disconnecting from chat...")

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
        if len(self.chatForm.chatFeed.values) > 20:
                self.chatForm.chatFeed.values = []
        self.chatForm.chatFeed.values.append('[SYSTEM] '+str(msg))
        self.chatForm.chatFeed.display()

    def sendMessage(self, _input):
        msg = self.chatForm.chatInput.value
        if msg == "":
            return False
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
                self.chatForm.chatFeed.values.append('{0}>  {1}'.format(self.nickname, msg))
                self.chatForm.chatFeed.display()
            else:
                self.sysMsg("You are not connected to a partner. Use /help to find out how to connect.")

    def exitApp(self):
        self.chatClient.send("%/quit")
        self.chatClient.disconn()
        self.chatServer.disconn()
        exit(1)
        

    def commandHandler(self, msg):
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

if __name__ == '__main__':
    chatApp = ChatApp().run()
    print("Started ChatApp...")