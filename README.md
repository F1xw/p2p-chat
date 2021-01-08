# P2P-Chat
P2P-Chat is a python based **peer-to-peer** chat client with a **command line interface**.

## Peer-to-peer vs. Client/Server

A regular **client/server** based chat:

```
         /<----\      /<----\
Client A        Server       Client B
         \---->/      \---->/
```

A **peer-to-peer** based chat:

```mermaid
         /<----\
Client A        Client B
         \---->/
```

As you can see, there  is no third-party server involved when using **peer-to-peer**.
All the messages you send and receive are private. They're only seen by your client and the client you are connected to.

![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `WARNING:` Nothing this client sends or receives is encrypted. Do only use it when connected to a private network.


# Installation

To install **P2P-Chat** simply download this repo.
```batch
git clone https://github.com/F1xw/p2p-chat
cd ./p2p-chat
```

## Requirements

P2P-Chat uses **npyscreen** to build its CLI. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install it:

```
pip install npyscreen
```
### For Windows users:

**npyscreen** uses the **curses** library which might not be pre-installed on windows.
Download the corresponding version for your installation from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses) and install it with [pip](https://pip.pypa.io/en/stable/).

## Usage
Run **/cli.py** to start the client.
```batch
python cli.py
```
You will be greeted with a slick, nostalgic CLI.
<br>
For debugging run **/cli.py** with **--debug** as an attribute.
```batch
python cli.py --debug
```
To change the server's port:
```batch
python cli.py --port [yourPort]
```

# Commands

**P2P-Chat** uses commands to setup and connect.
Try **/help** to get a list of all available commands.


## Connect to a peer

Use **/connect [host]&nbsp;[port]** to connect to a peer. The client will try to connect for 5 seconds. 
You will have to set your nickname before connecting using [/nick](#nickname)

## Disconnect

Use **/disconnect** to close the current connection.

## Nickname

Use **/nick [nickname]** to set your nickname. Updating your nickname while a connection is active will send your new name to the connected peer.

## Quit

Use **/quit** to quit the app.

## Help

Use **/help** to get a list of all available commands.

