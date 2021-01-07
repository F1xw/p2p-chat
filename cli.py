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
        self.chatFeed = self.add(npyscreen.MultiLineEdit, name="Feed", editable=False)
        self.chatInput = self.add(ChatInput, name="Input", footer="Enter -> Senden", rely=25)
        self.chatInput.entry_widget.handlers.update({curses.ascii.CR: self.exit_app})

    def send_message(self, _input):
        msg = self.chatInput.value
        chatClient.send(msg)

    def exit_app(self, _input):
        exit(0)

class ChatInput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class ChatApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', setupForm, name='Chat Setup')
        self.addForm('CHAT', chatForm, name='Peer-2-Peer Chat')
        self.chatServer = server.Server()
        self.chatServer.daemon = True
        self.chatServer.start()

    def startClient(self, nickname, ip, port):
        self.chatClient = client.Client(nickname, ip, port)
        self.chatClient.start()
        

if __name__ == '__main__':
    chatApp = ChatApp().run()
    print("Started ChatApp...")