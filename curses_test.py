import curses
import os
import socket
import threading
import time
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

UNKNOWN = "UNKNOWN\n".encode("utf-8")
SEND_OK = "SEND-OK\n".encode("utf-8")
DELIVERY = "DELIVERY".encode("utf-8")

# Failed implementation of a counter decorator for LINES on cprint and cinput
# def increment(val):
#     def increment_lines(func):
#         global LINES
#         def helper(*args, **kwargs):
#             global LINES
#             res = func(*args, **kwargs)
#             LINES = val + 1
#             return res
#         return helper
#     return increment_lines

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

def new_msg(sender, msg_type, content="", receiver=None):
    """Quick constructor for new messages to sent to the server"""

    return Message(sender, msg_type, content=content, receiver=receiver).to_json().encode('utf-8')


def check_screen_size(stdscr):
    """To be ran by a thread keeping check of the terminal size.
    Will resize the screens if it does change"""

    global HEIGHT, WIDTH
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

    # remember = cinput("Do you want to remember your login details? (y/n): ")

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
            return
        
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
                    string_bytes = new_msg(user, msg.msg_type)
                    continue

                err_msg = ""
                if response.message_type == "BAD-RQST-BODY": err_msg = "invalid"
                elif response.message_type == "UNKNOWN":     err_msg = "not known"
                else:                                        err_msg = "taken"
                username = cinput(screen_inner, 0, LINES, f'Username is {err_msg}, please enter another: ')
                user.name = username
                string_bytes = new_msg(user, msg.msg_type)
    
    LINES += 1
    cprint(screen_inner, 0, LINES, f"Welcome {user.name}!", SUC)
    # print home screen and initiate respective functions
    return True


def run_main():
    pass


def setup_main_screen(stdscr):
    """Sets up screens by clearing and adding borders etc"""

    global HEIGHT, WIDTH, LINES, screen_inner, input_outer, input_inner

    stdscr.clear()
    screen_inner.clear()
    input_outer.clear()
    input_inner.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    input_outer.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    LINES = 0

    with open('Logos/logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1

    screen_inner.addstr(LINES,0, "-"*(WIDTH-5))
    LINES += 1

    stdscr.refresh()
    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()  
    return


def resize_and_setup(stdscr):
    """Resizes the screens and prints the new layout"""

    set_sizes(stdscr)

    screen_inner.resize(IS_HEIGHT, IS_WIDTH)
    input_outer.resize(OI_HEIGHT, OI_WIDTH)
    input_inner.resize(II_HEIGHT, II_WIDTH)

    setup_main_screen(stdscr)
    return


def main(stdscr):
    """Main function"""

    global HEIGHT, WIDTH, LINES, screen_inner, input_outer, input_inner    
    create_screens(stdscr)
    setup_login_screen(stdscr)
    login = get_login_credentials()
    run_login(login)
    setup_main_screen(stdscr)
    run_main()
    # t = threading.Thread(target=check_screen_size, args=(stdscr,), daemon=True)
    # t.start()
    stdscr.getch()
    return

wrapper(main)