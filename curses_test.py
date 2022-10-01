import curses
import os
import threading
import time
from curses import wrapper

WAI = "."
INF = "*"
SUC = "+"
ERR = "!"
INP = ">"
SER = "S"

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
    global screen_inner, input_outer, input_inner
    curses.echo()

    set_sizes(stdscr)

    screen_inner = curses.newwin(IS_HEIGHT, IS_WIDTH, 1, 2)
    input_outer = curses.newwin(OI_HEIGHT, OI_WIDTH, HEIGHT-(OI_HEIGHT)-1, 2)
    input_inner = curses.newwin(II_HEIGHT, II_WIDTH, HEIGHT-(OI_HEIGHT), 3)
    return

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

def resize_and_setup(stdscr):
    set_sizes(stdscr)

    screen_inner.resize(IS_HEIGHT, IS_WIDTH)
    input_outer.resize(OI_HEIGHT, OI_WIDTH)
    input_inner.resize(II_HEIGHT, II_WIDTH)

    setup_screens(stdscr)
    return

def cprint(screen, text, pre=INF, x=0, y=0):
    screen.addstr(y, x, f"[{pre}] {text}")
    screen.refresh()
    return

def main(stdscr):
    global HEIGHT, WIDTH, screen_inner, input_outer, input_inner    
    create_screens(stdscr)
    setup_screens(stdscr)

    # t = threading.Thread(target=check_screen_size, args=(stdscr,), daemon=True)
    # t.start()

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