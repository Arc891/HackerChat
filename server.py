import socket
import threading

class BAD_RQST_BODY(Exception):
    def __init__(self):
        pass

class UNKNOWN(Exception):
    def __init__(self):
        pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = '127.0.0.1'
port = 5378
host_port = (host, port)
server.bind(host_port)

print("Server turned ON")
server.listen(100)

clients = []
usernames = []

def error_handler(connection, address, err_type):
    print("Exception", err_type, "sent to", address)
    connection.send((err_type + '\n').encode('utf-8'))
    return

def disconnect_client(connection):
    pop_index = 0 - (len(clients) - clients.index(connection))
    clients.pop(pop_index)
    usernames.pop(pop_index)
    return

def check_socket(connection):
    while True:
        try:
            connection.send(b'')
        except:
            return
    
    
def client_setup(connection, address):
    if len(clients) >= 100:
        connection.send(("BUSY\n").encode('utf-8'))
        return
    
    data = connection.recv(4096)
    decoded_data = data.decode("utf-8")

    username = ''
    
    if decoded_data[:10] == 'HELLO-FROM':
        for char in decoded_data[11:]:
            if ((ord(char) > 64 and ord(char) < 91) or   #Capital letters
                (ord(char) > 96 and ord(char) < 123) or  #Lower case letters
                (ord(char) > 47 and ord(char) < 58)):    #Numbers
                username += char 
            
            elif char == '\n':
                break
            
            else:
                error_handler(connection, address, "BAD-RQST-BODY")
                return

        if username not in usernames:
            clients.append(connection)
            usernames.append(username)
            connection.send((f'HELLO {username}\n').encode('utf-8'))
            client_thread(connection, address)
        
        else:
            error_handler(connection, address, "IN-USE")
            return

    else:
        error_handler(connection, address, "BAD-RQST-HDR")
        return

def client_thread(connection, address):
    print(address, "has started it's thread.")        
    sock_online = threading.Thread(target=check_socket, args=(connection,))
    sock_online.start()

    while sock_online.is_alive():       
        try:
            data = connection.recv(4096)

            if data == ("WHO\n").encode("utf-8"):                        
                user_string = ""

                for user in range(len(usernames)):
                    if (user != len(usernames) - 1):
                        user_string += usernames[user] + ", "
                    else:
                        user_string += usernames[user]

                connection.send(("WHO-OK " + user_string + "\n").encode("utf-8"))
            
            elif data[:5] == ("SEND ").encode("utf-8"):
                message = data[5:].decode("utf-8")
                send_message = ""

                split_message = message.split()
                receiver = split_message[0]
                
                if len(split_message) == 1:
                    raise BAD_RQST_BODY()
                else:
                    for x in split_message[1:]:
                        send_message += x + " "
                            
                if receiver not in usernames:
                    raise UNKNOWN()
                else: 
                    con_index = usernames.index(receiver)
                    sender_index = clients.index(connection)
                    
                    connection.send(("SEND-OK\n").encode("utf-8"))
                    clients[con_index].send(("DELIVERY " + usernames[sender_index] + " " +  send_message + "\n").encode("utf-8"))
                    
            elif data == b'\n':
                disconnect_client(connection)
                print("Client disconnected")
                return

            elif not data:
                break

        except UNKNOWN:
            print("Exception UNKNOWN sent")
            connection.send(('UNKNOWN\n').encode('utf-8'))
        
        except BAD_RQST_BODY:
            print("Exception BAD-RQST-BODY sent")
            connection.send(('BAD-RQST-BODY\n').encode('utf-8'))

        except ConnectionResetError:
            disconnect_client(connection)
            print("Client disconnected forcibly")
            return
    
    disconnect_client(connection)
    print("Client disconnected")
    return


while True:
    connected, address = server.accept()

    print(address, "has connected.")

    t = threading.Thread(target=client_setup, args=(connected, address))
    t.start()

server.close()