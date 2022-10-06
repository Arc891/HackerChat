## Login screen
```
+---------------------------------------------------------------+
| {1}   __  __           __             ________          __    |
|      / / / /___ ______/ /_____  _____/ ____/ /_  ____ _/ /_   |
|     / /_/ / __ `/ ___/ //_/ _ \/ ___/ /   / __ \/ __ `/ __/   |
|    / __  / /_/ / /__/ ,< /  __/ /  / /___/ / / / /_/ / /_     |
|   /_/ /_/\__,_/\___/_/|_|\___/_/   \____/_/ /_/\__,_/\__/     |
|                                                               |
| [*] Instructions...                                           |
|---------------------------------------------------------------|
| [>] Login/register? (l/r): r                                  |
| [>] Enter your name: Arc891                                   |
| [>] Enter your password: ...                                  |
| [>] Confirm your password: ...                                |
| [>] Do you want to remember your login details? (y/n):        |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
+---------------------------------------------------------------+
```

### Screens:
1. Title screen with instructions
2. Login messages


### Capabilities:
Screen 1:
- [ ]  Dynamic title art
- [x]  Stationary, full screen, print instructions and seperating line
- [x]  Print welcome and instructions
- [x]  Inputs done in line


### TODO:
- [x]  Make sure printing inputs works and looks good
- [ ]  Add remember login details


## Home screen
```
+---------------------------------------------------------------+
| {1}   __  __           __             ________          __    |
|      / / / /___ ______/ /_____  _____/ ____/ /_  ____ _/ /_   |
|     / /_/ / __ `/ ___/ //_/ _ \/ ___/ /   / __ \/ __ `/ __/   |
|    / __  / /_/ / /__/ ,< /  __/ /  / /___/ / / / /_/ / /_     |
|   /_/ /_/\__,_/\___/_/|_|\___/_/   \____/_/ /_/\__,_/\__/     |
|                                                               |
| [*] Instructions...                                           |
|---------------------------------------------------------------|
| {2}                                                           |
| [>] Chat with x                                               |
| [>] Group chat with a,b,c                                     |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|---------------------------------------------------------------|
| {3}                                                           |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| +-----------------------------------------------------------+ |
| | {4}                                                       | |
| | > ...                                                     | |
| |                                                           | |
| +-----------------------------------------------------------+ |
+---------------------------------------------------------------+
```

### Screens:
1. Title screen with instructions
2. List of personal and group chats
3. Where commands get shown with output and server messages are displayed
4. Input box for commands and messages


### Capabilities:
Screen 1:
- [ ]  Dynamic title art -/- Might not be a good idea considering the size of the title art
- [ ]  Stationary, needs to be 1/6th of screen height
- [ ]  Print instructions, check amount of lines available (?)

Screen 2:
- [ ]  Scrollable display -> needs to be a pad
- [ ]  Needs to be 1/3rd - 1/4th of screen height

Screen 3:
- [ ]   Scrollable display -> needs to be a pad
- [ ]   Needs to be the rest of the height of the screen until input box

Screen 4:
- [ ]  Scrollable input box -> needs to be a pad
- [ ]  Needs to be 1/6th of screen height


### TODO:
- [ ]  Figure out pads
- [ ]  Figure out scrolling in pads
- [ ]  Figure out commands for entering chats and scrolling through chats

## Chat screen
```
+---------------------------------------------------------------+
| [<custom icon?>#] Ezra Hulsman --> Could try ASCII art name   |
| [...] Last online: now/today/yesterday/some time ago/23:06    |
| [...] Group info, usernames, description                      |
| [*]  Typing...                                                |
|---------------------------------------------------------------|
| {2}                                                           |
| [22:12:53 >] Hi! How are you                                  |
|                                                               |
|                    Yooo doing good man! How r u? [22:14:42 <] |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| +-----------------------------------------------------------+ |
| | {3}                                                       | |
| | > ...                                                     | |
| |                                                           | |
| +-----------------------------------------------------------+ |
+---------------------------------------------------------------+
```

### Screens:
1. Name and status of chat
2. Chat messages
3. Input box for messages


### Capabilities:
Screen 1:
- [ ]  Display name -> perhaps ASCII art ? (JavaScript yank output from [here](https://patorjk.com/software/taag/#p=display&f=Slant&t=) or with [API](https://textart.io/api/figlet#), could use only first name/word if it's too long)
- [ ]  Stationary, needs to be 1/6th - 1/10th of screen height (depending on the ascii art)
- [ ]  Show online status and perhaps keep track of last seen times (general or specific?) -- personal chats only
- [ ]  Show group info (members, group name, group description, group icon?) -- group chats only

Screen 2:
- [ ]  Scrollable display -> needs to be a pad
- [ ]  Print all messages from history
- [ ]  Give each message a timestamp and sender name in group chats
- [ ]  Use (perhaps user chosen) colors for each user in chats

Screen 3:
- [ ]  Scrollable input box -> needs to be a pad

### TODO:
- [ ]  Check possibility of using ASCII art for names
- [ ]  Add color support within user maybe?
- [ ]  Create a way to keep track of last seen times
- [ ]  Define what time format to use for messages and last seen
- [ ]  In-chat commands? 
- [ ]  Creating group chats and what to do with their names if ASCII art is used


