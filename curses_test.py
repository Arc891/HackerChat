#!/usr/bin/env python3

import curses
import os
import socket
import threading
import time
from Classes.chatmessage import ChatMessage, ChatMessageDecoder
from Classes.user import *
from Classes.message import *
from hashlib import sha256
from curses import wrapper

WAI = "."
INF = "*"
SUC = "+"
ERR = "!"
INP = ">"
SER = "S"

SIGNUP = False

LINES = 0

HOST = '127.0.0.1'      # The server's hostname or IP address
PORT = 5378             # The port used by the server
host_port = (HOST, PORT)

def cprint(screen, x=0, y=0, text="", pre=INF):
    """Custom print function in style of the terminal onto a specific screen, 
    taking a 3rd parameter which defines the icon between the square brackets. """

    global LINES
    screen.addstr(y, x, f"[{pre}] {text}")
    screen.refresh()
    if y == LINES: LINES += 1
    return


def cinput(screen, x=0, y=0, text="", pwd=False):
    """Custom input function in style of the terminal in a specific screen,
    taking a 3rd parameter checking if the input is going to be a password,
    if so, the input will be hidden while typed."""
    
    global LINES
    if pwd: curses.noecho()
    cprint(screen, x, y, text, INP)
    inp = screen.getstr()
    curses.echo()
    if y == LINES: LINES += 1
    return inp.decode('utf-8')


def new_msg(sender: User, msg_type: str, content: str = "", receiver: User = None):
    """Quick constructor for new messages to sent to the server"""
    return Message(sender, msg_type, content, receiver).to_json().encode('utf-8')



def check_screen_size(stdscr):
    """To be ran by a thread keeping check of the terminal size.
    Will resize the screens if it does change"""

    global HEIGHT, WIDTH

    HEIGHT, WIDTH = stdscr.getmaxyx()

    while True:
        w, h = os.get_terminal_size()
        if h != HEIGHT or w != WIDTH:
            resize_and_setup(stdscr)


def set_sizes(stdscr):
    """Sets the size values of all the pads and screens based on the current terminal size"""

    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    HEIGHT, WIDTH = stdscr.getmaxyx()
    IS_HEIGHT = HEIGHT - 2
    IS_WIDTH  = WIDTH - 4
    OI_HEIGHT = HEIGHT // 6
    OI_WIDTH  = WIDTH - 4
    II_HEIGHT = OI_HEIGHT - 2
    II_WIDTH  = OI_WIDTH - 2

    IS_HEIGHT -= OI_HEIGHT
    return


def create_screens(stdscr):
    """Creates the physical screens that the application will be made out of"""

    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    global screen_inner, input_outer, input_inner
    curses.echo()

    set_sizes(stdscr)

    screen_inner = curses.newwin(IS_HEIGHT, IS_WIDTH, 1, 2)
    input_outer = curses.newwin(OI_HEIGHT, OI_WIDTH, HEIGHT-(OI_HEIGHT)-1, 2)
    input_inner = curses.newwin(II_HEIGHT, II_WIDTH, HEIGHT-(OI_HEIGHT), 3)
    return




def create_credentials_file(user: User, remember="n"):
    with open("config/credentials.txt", "w") as f:
        f.write(f"username={user.name}\n")
        f.write(f"password={user.password}\n")
        f.write(f"remember={remember}\n")
    f.close()

def return_credentials_file():
    if os.path.isfile("config/credentials.txt"):
        vals = []
        with open("config/credentials.txt", "r") as f:
            for _ in range(3):
                vals.append(f.readline().strip().split("=")[1])
        f.close()
        if vals[2] == "y":
            return User(vals[0], vals[1]) 
        elif vals[2] == "n":
            return None
        elif vals[2] == "N":
            return False
    return None

def setup_login_screen(stdscr):
    """Sets up screens by clearing and adding borders etc"""

    global HEIGHT, WIDTH, LINES, screen_inner

    stdscr.clear()
    screen_inner.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    LINES = 0

    with open('Logos/logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1 

    screen_inner.addstr(LINES,0, "-"*(WIDTH-4))
    LINES += 1
    stdscr.refresh()
    screen_inner.refresh()
    return



def get_login_credentials():
    """Gather login credentials and return them in a Message to run with run_login"""

    global SIGNUP, LINES, screen_inner
    
    creds = return_credentials_file()
    if creds: return Message(creds, "LOGIN")

    while True:
        login_type = cinput(screen_inner, 0, LINES, "Do you want to login or register? (l/r): ")
        if login_type == "l":
            SIGNUP = False
            break
        elif login_type == "r":
            SIGNUP = True
            break
        else:
            cprint(screen_inner, 0, LINES, "Invalid input. Try again.", ERR)
            continue
    
    user = cinput(screen_inner, 0, LINES, "Enter your name: ")
    pwd = cinput(screen_inner, 0, LINES, "Enter your password: ", pwd=True)

    while SIGNUP:
        if pwd == "": 
            pwd = cinput(screen_inner, 0, LINES, "Enter your password: ", pwd=True)
        
        pwd_check = cinput(screen_inner, 0, LINES, "Confirm your password: ", pwd=True)
        
        if pwd != pwd_check:
            cprint(screen_inner, 0, LINES, "Passwords do not match. Try again.", ERR)
            pwd = ""
            continue
        else: 
            break

    pwd = sha256(pwd.encode("utf-8")).hexdigest()

    if creds == None:
        remember = cinput(screen_inner, 0, LINES, "Do you want to remember your login details? ([y]es/[n]o/[N]ever): ")
        create_credentials_file(User(user, pwd), remember)

    msg_type = "SIGNUP" if SIGNUP else "LOGIN"
    return Message(User(user, pwd), msg_type)
    
def run_login(msg: Message):
    """Connects with the server and tries to login with the given credentials.\n
    Also handles any errors that might be returned when attempting login."""

    global SIGNUP, LINES, screen_inner

    user = msg.sender
    string_bytes = msg.to_json().encode("utf-8")

    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        LINES += 1
        cprint(screen_inner, 0, LINES, f"Connecting to {HOST}:{PORT}...", INF)
        
        try:    
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            cprint(screen_inner, 0, LINES, f"Connection to {HOST}:{PORT} failed. Server is most likely offline.", ERR)
            return False
        
        cprint(screen_inner, 0, LINES, "Connected.", SUC)

        s.sendall(string_bytes)
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")

        try:
            response = Message(**json.loads(decoded_data))
        except json.decoder.JSONDecodeError:
            pass
        finally:
            if response.message_type == "HELLO":
                string_bytes = b''
                break

            else:
                s.close()
                if response.message_type == "BAD-PASS":
                    pwd = cinput(screen_inner, 0, LINES, 'Password is incorrect, try again: ', pwd=True)
                    user.password = sha256(pwd.encode("utf-8")).hexdigest()
                    string_bytes = new_msg(user, msg.message_type)
                    continue

                err_msg = ""
                if response.message_type == "BAD-RQST-BODY": err_msg = "invalid"
                elif response.message_type == "UNKNOWN":     err_msg = "not known"
                else:                                        err_msg = "taken"
                username = cinput(screen_inner, 0, LINES, f'Username is {err_msg}, please enter another: ')
                user.name = username
                string_bytes = new_msg(user, msg.message_type)
    
    LINES += 1
    cprint(screen_inner, 0, LINES, f"Welcome {user.name}!", SUC)
    time.sleep(1)
    return (s, user)


def setup_home_screen():
    """Sets up screens by clearing and adding borders etc"""

    global HEIGHT, WIDTH, LINES, screen_inner, input_outer, input_inner

    instructions = ['Type !quit to exit.', 
                    'Type !chat <chat> to go to said chat.',
                    'Type !help to see all available commands.'] 

    screen_inner.clear()
    input_outer.clear()
    input_inner.clear()

    input_outer.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    LINES = 0

    with open('Logos/logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1
        f.close()
    
    for line in instructions:
        screen_inner.addstr(LINES, (WIDTH-len(line))//2-1, line, curses.A_BOLD)
        LINES += 1


    screen_inner.addstr(LINES,0, "-"*(WIDTH-4))
    LINES += 1

    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()  
    return

def print_help():
    """Prints help to the screen"""

    global LINES, screen_inner

    help = ['!help: Prints this help message.',
            '!quit: Quits the program.',
            '!online: Prints all online users.',
            '!chat <username/groupname>: Opens chat with <username>.']
    
    for line in help:
        cprint(screen_inner, 0, LINES, line)

    screen_inner.refresh()
    return


def data_receive(s, host_port):
    """Receives data from the server and prints it to the screen"""

    while s.connect_ex(host_port) != 9:
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")
        
        if not data:
            break
        
        msg = Message(**json.loads(decoded_data))

        if msg.message_type == "UNKNOWN":
            cprint(screen_inner, 0, LINES, "Data is unknown", ERR)
            time.sleep(0.1)
            try:
                s.getsockname()
            except OSError:
                break
            cprint(screen_inner, 0, LINES, decoded_data[:len(decoded_data)-1], SER)
            
        elif msg.message_type == "SEND-OK":
            cprint(screen_inner, 0, LINES, data, SER)
        
        elif msg.message_type == "DELIVERY":
            cprint(screen_inner, 0, LINES, "Data is delivered", SER)
            cprint(screen_inner, 0, LINES, msg.content)
            
        elif msg.message_type == "WHO-OK":
            cprint(screen_inner, 0, LINES, f"Online: {msg.content}", SER)
        else:
            cprint(f"Random data received: {msg.content}", SER)


def print_chat_messages(user: User, receiver: User = User('')):
    """Prints chat messages to the screen"""

    global LINES, screen_inner, HEIGHT, WIDTH

    for chats in os.listdir('chats'):    
        if user.name in chats and receiver.name in chats:
            with open(f'chats/{chats}', 'r') as f:
                for message in f:
                    msg = ChatMessage(**json.loads(message, cls=ChatMessageDecoder))
                    pre = lambda s, f="", b="": f"{f}[{s} {msg.sender} {msg.time_as_string()}]{b}"

                    msg_list = msg.content.split()
                    j = 0

                    if msg.sender != user.name:
                        for i in range(len(msg_list)):
                            rest = ' '.join(msg_list[j:]) + pre('<', f=' ')
                            if len(rest) <= IS_WIDTH-10:
                                screen_inner.addstr(LINES, IS_WIDTH-len(rest), rest)
                                LINES += 1
                                break
                            if len(' '.join(msg_list[j:i])) > IS_WIDTH-10:
                                screen_inner.addstr(LINES, 10, ' '.join(msg_list[j:i-1]))
                                LINES += 1
                                j = i-1
                        
                    else: 
                        for i in range(len(msg_list)):
                            if i+1 == len(msg_list):
                                add = pre('>', b=' ') if j == 0 else ""
                                screen_inner.addstr(LINES, 0, add + ' '.join(msg_list[j:]))
                                LINES += 1
                                break
                            if j == 0:
                                if i+1 < len(msg_list):
                                    if len(pre('>', b=' ') + ' '.join(msg_list[j:i+1])) > IS_WIDTH-10:
                                        screen_inner.addstr(LINES, 0, pre('>', b=' ') + ' '.join(msg_list[j:i+1]))
                                        LINES += 1
                                        j = i+1
                            elif len(' '.join(msg_list[j:i])) > IS_WIDTH-10:
                                screen_inner.addstr(LINES, 0, ' '.join(msg_list[j:i-1]))
                                LINES += 1
                                j = i-1
    
    screen_inner.refresh()
    return


def run_home(s: socket.socket, user: User):
    """Runs the main screen of the chat application"""

    global LINES, screen_inner, input_inner, input_outer, HEIGHT, WIDTH

    t = threading.Thread(target=data_receive, args=(s, host_port), daemon=True)
    t.start()

    

    while True:
        input_inner.addstr(0, 0, "$", curses.A_BOLD)
        msg = input_inner.getstr(0,2).decode("utf-8")
        
        if not msg: continue

        if msg == "!quit":
            s.sendall(new_msg(user, "LOGOUT"))
            time.sleep(0.1)
            s.close()
            break

        elif msg == "!help":
            print_help()

        elif msg == "!online":
            s.sendall(new_msg(user, "WHO"))

        elif msg == "!clear":
            screen_inner.clear()
            setup_home_screen()

        elif msg == "!chat":
            print_chat_messages(user)

        elif msg.startswith("!chat"):
            try:
                msg = msg.split()
                to_send = new_msg(user, "SEND", ' '.join(msg[2:]), User(msg[1]))
                s.sendall(to_send)
            except IndexError:
                cprint(screen_inner, 0, LINES, "Please enter a username to chat with.", ERR)
        
        else:
            cprint(screen_inner, 0, LINES, "Unknown command. Type !help to see all available commands.", ERR)
        
        input_inner.clear()
        input_inner.refresh()
        time.sleep(1/100)


def resize_and_setup(stdscr):
    """Resizes all the screens and pads and sets up the new ones"""

    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    global screen_inner, input_outer, input_inner

    set_sizes(stdscr)

    screen_inner.resize(IS_HEIGHT, IS_WIDTH)
    input_outer.resize(OI_HEIGHT, OI_WIDTH)
    input_inner.resize(II_HEIGHT, II_WIDTH)

    screen_inner.mvwin(1, 2)
    input_outer.mvwin(HEIGHT-(OI_HEIGHT)-1, 2)
    input_inner.mvwin(HEIGHT-(OI_HEIGHT), 3)

    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()
    return


def main(stdscr):
    """Main function"""

    global HEIGHT, WIDTH, LINES, screen_inner, input_outer, input_inner    
    
    t = threading.Thread(target=check_screen_size, args=(stdscr,), daemon=True)
    t.start()
    
    create_screens(stdscr)
    setup_login_screen(stdscr)
    login = get_login_credentials()
    (s, user) = run_login(login)
    setup_home_screen()
    run_home(s, user)
    stdscr.getch()
    return

wrapper(main)