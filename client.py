from code import interact
import socket
import threading
import time
import os

from psutil import boot_time

T_WIDTH = os.get_terminal_size().columns
T_HEIGHT = os.get_terminal_size().lines

LOGO_FULL_WIDTH = 'logo-full-width.txt' # 57 chars wide
LOGO_HALF_WIDTH = 'logo-half-width.txt' # 35 chars wide

UNKNOWN = "UNKNOWN\n".encode("utf-8")
SEND_OK = "SEND-OK\n".encode("utf-8")
DELIVERY = "DELIVERY".encode("utf-8")

# with open('logo-full-width.txt', 'r') as f:
#     for l in f:
#         print(len(l))

"""
A function to keep track of the terminal width, 
and will resize the current display if the width changes.
"""
def check_width(width):
    while True:
        if os.get_terminal_size().columns is not width:
            T_WIDTH = os.get_terminal_size().columns
            width = T_WIDTH
            print_interface(width)

def print_logo_middle(width = T_WIDTH):
    # The full logo is 57 characters wide, so accounting for the bars on the side totals to 59 chars to display
    logo_name = LOGO_FULL_WIDTH if width >= 59 else LOGO_HALF_WIDTH 
    with open(logo_name, 'r') as f:
        for line in f:
            print(f"| {line[:-1]:^{width-4}} |")
    # # If T_WIDTH is uneven, then the logo will be centered, otherwise if it's even it will be off by one, so add an optional extra space
    # uneven_spaces = " " if (width % 2 == 0) else ""
    
    # with open(logo_name, 'r') as logo:
    #     for l in logo:
    #         offset = ((width - 2) - len(l)) // 2
    #         filler = " " * (offset)

    #         print(f"|{filler}{l[:-1]}{filler}{uneven_spaces}|")


def print_interface(width = T_WIDTH):
    line = "-" * width
    print(line)
    
    print_logo_middle(width)
    
    instructions = ['Type !quit to exit.', 'Type !who to see who is in the chatroom.', 'Type @username to send a message to username.']
    for i in instructions:
        print(f"| {i:<{width-3}}|")
    

    # print(interface, bottom_line, sep="\n")

print_interface()

def data_receive(s, host_port):
    while s.connect_ex(host_port) != 9:
        data = b''
        while b'\n' not in data:
            data += s.recv(2)
        decoded_data = data.decode("utf-8")
        if not data:
            break
        elif data == UNKNOWN:
            print("Data is unknown")
            time.sleep(0.1)
            try:
                s.getsockname()
            except OSError:
                break
            print('Server:', decoded_data[:len(decoded_data)-1])
            break
        elif data == SEND_OK:
            # print("Data is send ok")
            print(data)
            break
        elif DELIVERY in data:
            print("Data is delivered")
            decoded_data = decoded_data.split(" ")
            
            print(decoded_data[1], end=": ")
            for word in decoded_data[2:-1]:
                print(word, end=" ")
            print("\n| > ", end=" ")
        else:
            print('| Server:', decoded_data[:len(decoded_data)-1])

def messenger_function():
    HOST = '127.0.0.1'      # The server's hostname or IP address
    PORT = 5378             # The port used by the server
    host_port = (HOST, PORT)

    user = input('What\'s your username? ')
    msg = " "
    hello = "HELLO-FROM " + user + "\n"
    who = "WHO\n"

    enter = True
    name = False

    string_bytes = hello.encode("utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while not name:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(host_port)
        s.sendall(string_bytes)
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")
        print('Server:', decoded_data[:len(decoded_data)-1])

        if data == ("HELLO " + user + "\n").encode("utf-8"):
            string_bytes = b''
            name = True
            break 

        else:
            print(data)
            s.close()
            if data == ("BAD-RQST-BODY\n").encode("utf-8"):
                user = input('Username is invalid, please enter another: ')
            else:
                user = input('Username is taken, please enter another: ')
            hello = "HELLO-FROM " + user + "\n"
            string_bytes = hello.encode("utf-8")
    
    t = threading.Thread(target=data_receive, args=(s, host_port), daemon=True)
    t.start()
    msg = " "
    print_interface()
    
    while msg != "!quit": 

        if not enter:
            print("|", end=" ")
            msg = input('> ').strip()

        enter = False

        if (msg == "!quit"):
            text_message = "SEND @ Bye! \n"
            string_bytes = text_message.encode("utf-8")
            s.sendall(string_bytes)
            time.sleep(0.1)
            s.close()
            break

        elif (msg == "!who"):
            string_bytes = who.encode("utf-8")

        elif (msg[0] == "@"):
            text_message = "SEND " + msg[1:] + " \n"
            string_bytes = text_message.encode("utf-8")         
            
        s.sendall(string_bytes)
        time.sleep(1/100)
       
    print(f"Cya later, {user}!")
    threading._shutdown()
    
    t.join()
    exit()

def main():
    messenger_function()


if __name__ == "__main__":
    print(T_WIDTH)
    t_width = threading.Thread(target=check_width, args=(T_WIDTH,), daemon=True)
    t_width.start()
    main()