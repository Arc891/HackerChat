import curses
import os
import threading
import time
import user
import message 
from curses import wrapper

WAI = "."
INF = "*"
SUC = "+"
ERR = "!"
INP = ">"
SER = "S"

LOGIN = False
SIGNUP = False


"""
Custom print function in style of the terminal onto a specific screen, 
taking a 3rd parameter which defines the icon between the square brackets. 
"""
def cprint(screen, text, pre=INF, x=0, y=0):
    screen.addstr(y, x, f"[{pre}] {text}")
    screen.refresh()
    return


"""
Custom input function in style of the terminal in a specific screen,
taking a 3rd parameter checking if the input is going to be a password,
if so, the input will be hidden while typed.
"""
def cinput(screen, msg, x=0, y=0, pwd=False):
    if pwd: curses.noecho()
    cprint(screen, msg, INP, x, y)
    inp = screen.getstr()
    curses.echo()
    return inp.decode('utf-8')

"""
Will be ran by a thread keeping check of the terminal size
Will resize the screens if it does change
"""
def check_screen_size(stdscr):
    global HEIGHT, WIDTH
    while True:
        w, h = os.get_terminal_size()
        if h != HEIGHT or w != WIDTH:
            resize_and_setup(stdscr)



"""
Sets the sizes of all the pads and screens based on the current terminal size
"""
def set_sizes(stdscr):
    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    HEIGHT, WIDTH = stdscr.getmaxyx()
    IS_HEIGHT = HEIGHT - 2
    IS_WIDTH = WIDTH - 4
    OI_HEIGHT = HEIGHT // 6
    OI_WIDTH = WIDTH - 4
    II_HEIGHT = OI_HEIGHT - 2
    II_WIDTH = OI_WIDTH - 2

    IS_HEIGHT -= OI_HEIGHT
    return


"""
Creates the physical screens that the application will be made out of
"""
def create_screens(stdscr):
    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    global screen_inner, input_outer, input_inner
    curses.echo()

    set_sizes(stdscr)

    screen_inner = curses.newwin(IS_HEIGHT, IS_WIDTH, 1, 2)
    input_outer = curses.newwin(OI_HEIGHT, OI_WIDTH, HEIGHT-(OI_HEIGHT)-1, 2)
    input_inner = curses.newwin(II_HEIGHT, II_WIDTH, HEIGHT-(OI_HEIGHT), 3)
    return



"""
Sets up screens by clearing and adding borders etc 
"""
def setup_login_screen(stdscr) -> int:
    global HEIGHT, WIDTH, screen_inner

    stdscr.clear()
    screen_inner.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    curr_lines = 0

    with open('logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1])
            curr_lines += 1 

    screen_inner.addstr(curr_lines,0, "-"*(WIDTH-4))

    stdscr.refresh()
    screen_inner.refresh()
    return curr_lines+1


def run_login(stdscr, lines):
    global LOGIN, SIGNUP, screen_inner
    
    while True:
        login_type = cinput(screen_inner, "Do you want to login or register? (l/r): ", 0, lines)
        lines += 1
        if login_type == "l":
            LOGIN = True
            break
        elif login_type == "r":
            SIGNUP = True
            break
        else:
            cprint(screen_inner, "Invalid input. Try again.", ERR)
            continue
    
    user = cinput(screen_inner, "Enter your name: ", 0, lines)
    lines += 1
    pwd = cinput(screen_inner, "Enter your password: ", 0, lines, pwd=True)
    lines += 1
    
    while SIGNUP:
        if pwd == "": 
            pwd = cinput(screen_inner, "Enter your password: ", 0, lines, pwd=True)
            lines += 1
        pwd_check = cinput(screen_inner, "Confirm your password: ", 0, lines, pwd=True)
        lines += 1
        if pwd != pwd_check:
            cprint(screen_inner, "Passwords do not match. Try again.", ERR, 0, lines)
            lines += 1
            pwd = ""
            continue
        else: 
            break

    # pwd = sha256(pwd.encode("utf-8")).hexdigest()

    # # remember = cinput("Do you want to remember your login details? (y/n): ")
    
    # u = User(user, pwd) 
    # msg_type = "SIGNUP" if SIGNUP else "LOGIN"
    # message2 = Message(u, msg_type)
    # # print(s)
    # # print(message2.to_json())

    # string_bytes = message2.to_json().encode("utf-8")


"""
Sets up screens by clearing and adding borders etc 
"""
def setup_screens(stdscr):
    global HEIGHT, WIDTH, screen_inner, input_outer, input_inner

    stdscr.clear()
    screen_inner.clear()
    input_outer.clear()
    input_inner.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    input_outer.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    with open('logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1])

    screen_inner.addstr(HEIGHT//2-1,0, "-"*(WIDTH-5))

    stdscr.refresh()
    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()  
    return


"""
Resizes the screens and prints the new layout
"""
def resize_and_setup(stdscr):
    set_sizes(stdscr)

    screen_inner.resize(IS_HEIGHT, IS_WIDTH)
    input_outer.resize(OI_HEIGHT, OI_WIDTH)
    input_inner.resize(II_HEIGHT, II_WIDTH)

    setup_screens(stdscr)
    return


"""
Main function
"""
def main(stdscr):
    global HEIGHT, WIDTH, screen_inner, input_outer, input_inner    
    create_screens(stdscr)
    # setup_screens(stdscr)
    lines = setup_login_screen(stdscr)
    run_login(stdscr, lines)
    # t = threading.Thread(target=check_screen_size, args=(stdscr,), daemon=True)
    # t.start()
    stdscr.getch()
    return
    line = 0
    while True:
        inp = input_inner.getstr(0, 0).decode('utf-8')
        
        if inp == "!q":
            break
        
        cprint(screen_inner, inp, INP, 0, line)
        input_inner.clear()

        screen_inner.refresh()
        input_inner.refresh() 
        line += 1
    

wrapper(main)