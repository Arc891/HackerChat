import curses
import os
import threading
import time
from curses import wrapper

def check_screen_size(stdscr):
    global HEIGHT, WIDTH
    while True:
        w, h = os.get_terminal_size()
        if h != HEIGHT or w != WIDTH:
            resize_and_setup(stdscr)


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

def create_screens(stdscr):
    global HEIGHT, WIDTH, IS_HEIGHT, IS_WIDTH, OI_HEIGHT, OI_WIDTH, II_HEIGHT, II_WIDTH
    global innerscreen, outerinput, innerinput
    curses.echo()

    set_sizes(stdscr)

    innerscreen = curses.newwin(IS_HEIGHT, IS_WIDTH, 1, 2)
    outerinput = curses.newwin(OI_HEIGHT, OI_WIDTH, HEIGHT-(OI_HEIGHT)-1, 2)
    innerinput = curses.newwin(II_HEIGHT, II_WIDTH, HEIGHT-(OI_HEIGHT), 3)
    return


def setup_screens(stdscr):
    global HEIGHT, WIDTH, innerscreen, outerinput, innerinput

    stdscr.clear()
    innerscreen.clear()
    outerinput.clear()
    innerinput.clear()

    stdscr.border("|", "|", "-", "-", "+", "+", "+", "+")
    outerinput.border("|", "|", "-", "-", "+", "+", "+", "+")
    
    with open('logo-full-width.txt', 'r') as f:
        for i, line in enumerate(f):
            innerscreen.addstr(i, (WIDTH-len(line))//2-1, line[:-1])

    innerscreen.addstr(HEIGHT//2-1,0, "-"*(WIDTH-5))

    stdscr.refresh()
    innerscreen.refresh()
    outerinput.refresh()
    innerinput.refresh()  
    return

def resize_and_setup(stdscr):
    set_sizes(stdscr)

    innerscreen.resize(IS_HEIGHT, IS_WIDTH)
    outerinput.resize(OI_HEIGHT, OI_WIDTH)
    innerinput.resize(II_HEIGHT, II_WIDTH)

    setup_screens(stdscr)
    return

def main(stdscr):
    global HEIGHT, WIDTH, innerscreen, outerinput, innerinput    
    create_screens(stdscr)
    setup_screens(stdscr)

    # t = threading.Thread(target=check_screen_size, args=(stdscr,), daemon=True)
    # t.start()

    while True:
        inp = innerinput.getstr(0, 0).decode('utf-8')
        
        if inp == "!q":
            break
        
        innerscreen.refresh()
        innerscreen.addstr(0,0, inp)
        innerinput.clear()
        innerinput.refresh() 
        innerscreen.refresh()
    

wrapper(main)