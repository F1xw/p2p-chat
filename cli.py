import npyscreen
import server
import client
import time
import curses

class setupForm(npyscreen.Form):
    def create(self):
        self.nickname = self.add(npyscreen.TitleText, name='Nickname>')
        self.partnerIP = self.add(npyscreen.TitleText, name='Partner IP>')
        self.partnerPort = self.add(npyscreen.TitleText, name='Partner Port>')

    def afterEditing(self):
        self.parentApp.startClient(self.nickname.value, self.partnerIP.value, self.partnerPort.value)
        self.parentApp.setNextForm("CHAT")

class chatForm(npyscreen.FormBaseNew):
    def create(self):

        event_handlers = {
            # STRG + Q -> Exit
            "^Q": self.exit_app
        }

        self.add_handlers(event_handlers)

        y, x = self.useable_space()
        self.chatFeed = self.add(npyscreen.BoxTitle, name="Feed", editable=False, max_height=23, scroll_slow=True)
        self.chatInput = self.add(ChatInput, name="Input", footer="Enter -> Senden", rely=25)
        self.chatInput.entry_widget.handlers.update({curses.ascii.CR: self.parentApp.send_message})

        self.chatFeed.values = []

    def exit_app(self, _input):
        exit(0)

class ChatInput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class ChatApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.mainForm = self.addForm('MAIN', setupForm, name='Chat Setup')
        self.chatForm = self.addForm('CHAT', chatForm, name='Peer-2-Peer Chat')
        self.chatServer = server.Server(self)
        self.chatServer.daemon = True
        self.chatServer.start()

    def startClient(self, nickname, ip, port):
        self.chatClient = client.Client(nickname, ip, port)
        self.chatClient.start()
        self.nickname = nickname

    def send_message(self, _input):
        if len(self.chatApp.chatForm.chatFeed.values) > 20:
                self.chatApp.chatForm.chatFeed.values = []
        msg = self.chatForm.chatInput.value
        if msg != '':
            self.chatClient.send(msg)
            self.chatForm.chatFeed.values.append('{0}>  {1}'.format(self.nickname, msg))
            self.chatForm.chatInput.value = ""
            self.chatForm.chatFeed.display()
            self.chatForm.chatInput.display()
        

if __name__ == '__main__':
    chatApp = ChatApp().run()
    print("Started ChatApp...")