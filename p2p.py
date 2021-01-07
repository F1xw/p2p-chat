from server import Server
from client import Client
import time

srv = Server()
srv.daemon = True
srv.start()
time.sleep(2)
cli = Client('F1xw2', 'localhost', 3333)
cli.start()