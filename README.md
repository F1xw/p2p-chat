# P2P-Chat
P2P-Chat is a python based **peer-to-peer** chat client with a **command line interface**.

# For your information:

```
As this project was only for demonstation purposes as part of my paper on p2p, I will no longer work on p2p-chat.
You may fork this repository to work on it yourself.
```


## Peer-to-peer vs. Client/Server

A regular **client/server** based chat:

```
         /<----\      /<----\
Client A        Server       Client B
         \---->/      \---->/
```

A **peer-to-peer** based chat:

```
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

P2P-Chat uses several python module. Make sure the package manager [pip](https://pip.pypa.io/en/stable/) is installed, so that p2p-chat can automatically install all required modules.

### For Windows users:

**npyscreen** uses the **curses** library which might not be pre-installed on windows.
Download the corresponding version for your installation from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses) and install it with [pip](https://pip.pypa.io/en/stable/).

## Usage
Run **/run.py** to start the client.
```batch
python run.py
```

You will be greeted with a slick, nostalgic CLI.

<i>Try resizing your terminal if the app chrashes instantly.</i>

<br>

To use **p2p-chat** follow these steps:
1. Set your nickname with [/nickname](#nickname)
2. Connect to a peer with [/connect](#Connect%20to%20a%20peer)

You are now able to send messages to the connected peer by typing them in and pressing enter. Take a look at all the other commands down below.
# Commands

**P2P-Chat** uses commands to setup and connect.
Try **/help** to get a list of all available commands.


## Connect to a peer

Use **/connect [host]&nbsp;[port]** to connect to a peer. The client will try to connect for 5 seconds. 
You will have to set your nickname before connecting using [/nick](#nickname)

<i>Example:</i>

```
/connect office-pc.local 3333
```


## Disconnect

Use **/disconnect** to close the current connection.

<i>Example:</i>

```
/disconnect
```

## Nickname

Use **/nick [nickname]** to set your nickname. Updating your nickname while a connection is active will send your new name to the connected peer.

<i>Example:</i>

```
/nick flowei
```


## Quit

Use **/quit** to quit the app.

<i>Example:</i>

```
/quit
```


## Port

Use **/port** to change the port your server runs on.

<i>Example:</i>

```
/port 3456
```


## Connectback

Use **/connectback** to connect to a peer without having to enter their hostname and port. This command is only available if your server receives a connection while your client is not connected.

<i>Example:</i>

```
/connectback
```


## Clear

Use **/clear** to clear the chat.

<i>Example:</i>

```
/clear
```

## Eval

Use **/eval [python code]** to execute python code within the app itself. The output will be relayed to the chat feed.

<i>Example:</i>

```
# Print the nickname of the connected peer
/eval print(self.peer)
```

```
# Generate a system message
/eval self.sysMsg("Hello from /eval!")
```

```
# Forcefully exit the app
/eval exit()
```

## Status

Use **/status** to get the current status of server and client.

<i>Example:</i>

```
/status
```

## Log

Use **/log** to log all messages sent and received during your session to a file.

<i>Example:</i>

```
/log
```

## Help

Use **/help** to get a list of all available commands.

<i>Example:</i>

```
/help
```

