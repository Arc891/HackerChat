# HackerChat
```
$ python3 hackerchat.py
>   __  __           __             ________          __ 
   / / / /___ ______/ /_____  _____/ ____/ /_  ____ _/ /_
  / /_/ / __ `/ ___/ //_/ _ \/ ___/ /   / __ \/ __ `/ __/
 / __  / /_/ / /__/ ,< /  __/ /  / /___/ / / / /_/ / /_  
/_/ /_/\__,_/\___/_/|_|\___/_/   \____/_/ /_/\__,_/\__/  
```
## What is HackerChat?

HackerChat is meant as a personal use CLI chat service, in which you can send small text messages from one client to another. The functionality is still basic, but is looking to expand with seperated chat rooms, chats being stored and dynamic interface.

### Personal chat
This is a chat program where you can send messages to people who are online, and receive their messages and server messages all in one screen. No chats are separated. Supports !who command to see who is online, and !quit to exit. This is the chat that will be my main focus going forward.

### Open chat
The open chat is a chat where you connect with the server, and enter a global chat where all messages get sent to everyone. I might add command possibilities like a Twitch chat, and see if I can extend this with the personal chats.

## Dependancies

- Python 3.6+
- curses module

## Functionality roadmap

### Personal chat

- [x]  Dynamic interface (for now, will refine later) --> Curses module
- [x]  Merge with open chat interface
- [x]  Login with username and password:
  -  [x] Change method of sending data to JSON
- [ ]  Implement Curses module for better interface
- [ ]  Seperate chats
- [ ]  Chat messages stored
- [ ]  Group chats
