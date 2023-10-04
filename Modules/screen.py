import curses
import os
from Modules.globals import *


#--# Custom prints #--#

def cprint(screen: curses.window, x: int=0, y: int=0, text: str="", pre: str=INF, stage: bool=False):
    """Custom print function in style of the terminal onto a specific screen, 
    taking a 'pre' parameter which defines the icon between the square brackets.\n
    Also supports a 'stage' parameter which if set to True will stage the text 
    to be printed on the next manual refresh."""

    global LINES
    add_front = f'[{pre}] ' if pre else NON
    text = text.strip('\n')
    to_print = f"{add_front}{text}"
    screen.addstr(y, x, to_print)
    if not stage: screen.refresh()
    if y == LINES: LINES += 1
    return


def cinput(screen: curses.window, x: int=0, y: int=0, text: str="", pwd: bool=False):
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




#--# Screen functions #--#

def check_screen_size(stdscr: curses.window):
    """To be ran by a thread keeping check of the terminal size.
    Will resize the screens if it does change"""

    global HEIGHT, WIDTH

    HEIGHT, WIDTH = stdscr.getmaxyx()

    while True:
        w, h = os.get_terminal_size()
        if h != HEIGHT or w != WIDTH:
            cprint(stdscr, 0, 0, "Resizing...", INF)
    #         curses.resizeterm(h, w)
            # resize_and_setup(stdscr)


def set_sizes(stdscr: curses.window):
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


def create_screens(stdscr: curses.window):
    """Creates the physical screens that the application will be made out of"""

    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    global screen_inner, input_outer, input_inner
    curses.echo()

    set_sizes(stdscr)

    screen_inner = curses.newwin(IS_HEIGHT, IS_WIDTH, 1, 2)
    input_outer = curses.newwin(OI_HEIGHT, OI_WIDTH, HEIGHT-(OI_HEIGHT)-1, 2)
    input_inner = curses.newwin(II_HEIGHT, II_WIDTH, HEIGHT-(OI_HEIGHT), 3)
    return


def setup_login_screen(stdscr: curses.window):
    """Sets up screens by clearing and adding borders etc"""

    global HEIGHT, WIDTH, LINES, screen_inner

    stdscr.clear()
    screen_inner.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    LINES = 0

    logo_name = LOGO_FULL_WIDTH if WIDTH >= 59 else LOGO_HALF_WIDTH

    with open(logo_name, 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1 

    screen_inner.addstr(LINES,0, "-"*(WIDTH-4))
    LINES += 1
    stdscr.refresh()
    screen_inner.refresh()
    return


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

    logo_name = LOGO_FULL_WIDTH if WIDTH >= 59 else LOGO_HALF_WIDTH

    with open(logo_name, 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1
    
    print_help(screen_inner, lambda x: (WIDTH-len(x))//2-1, instructions)

    cprint(screen_inner, 0, LINES, "-"*(WIDTH-4), NON)
    #cprint(screen_inner, 0, LINES, f"{screen_inner.__dir__} {curses.newpad(1000,IS_WIDTH).__dir__}", NON)

    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()  
    return


def setup_chat_screen():
    """Sets up screens by clearing and adding borders etc"""

    global HEIGHT, WIDTH, LINES, screen_inner, input_outer, input_inner

    screen_inner.clear()
    input_outer.clear()
    input_inner.clear()

    input_outer.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    LINES = 0

    logo_name = LOGO_FULL_WIDTH if WIDTH >= 59 else LOGO_HALF_WIDTH

    with open(logo_name, 'r') as f:
        for i, line in enumerate(f):
            screen_inner.addstr(i, (WIDTH-len(line))//2-1, line[:-1], curses.A_BOLD)
            LINES += 1
    
    cprint(screen_inner, 0, LINES, "-"*(WIDTH-4), NON)

    screen_inner.refresh()
    input_outer.refresh()
    input_inner.refresh()  
    return