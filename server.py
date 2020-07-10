from socket import AF_INET,socket,SOCK_STREAM , gethostname, gethostbyname
from threading import Thread
import pandas as pd
import time
import pickle
HOST_NAME = gethostname()
IP = gethostbyname(HOST_NAME)
print(IP)
PORT = 5051
BUFSIZ = 1024
HEADER_SignUp = 'SIGNUP'
HEADER_already_exist = 'AlreadyExist'
HEADER_SignIn = 'SIGNIN'
HEADER_Start = 'START'
HEADER_msg ='MSG'
HEADER_REC = 'REC'
HEADER_Search = 'SEARCH'
HEADER_NonEx = 'SEARCH_NonEXIST'

ADDR = (IP, PORT)
clients = {}
addresses = {}
usernames = {}
passwords = []
fullnames = []
list_of_existing_usernames =[]
Server = socket(AF_INET, SOCK_STREAM)
Server.bind(ADDR)

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        global Server
        client, client_address = Server.accept()
        if not client in addresses.keys():
             addresses[client] = client_address
        Thread(target=handle_client, args=(client,client_address,)).start()

def sendAndReceive(client,sender):
    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        if msg.startswith(HEADER_Search):
            msg = msg.replace(HEADER_Search,'')
            if msg in list_of_existing_usernames:
               client.send(bytes(HEADER_Search+usernames[msg][1]+'||'+msg, "utf8"))

            else:
               client.send(bytes(HEADER_NonEx, "utf8"))
              #  continue

        elif msg.startswith(HEADER_msg):
            full_msg = msg.replace(HEADER_msg, '')
            msg_obtained = full_msg.split('\n')
            receiver_of_msg = msg_obtained[0]
            content_of_msg = msg_obtained[1]
            if not sender == receiver_of_msg:
                for key  in clients.keys() :
                    if receiver_of_msg in clients[key]:
                        key.sendall(bytes(HEADER_msg + sender + HEADER_REC + content_of_msg, "utf8"))
            else:
                 client.sendall(bytes(HEADER_msg + sender + HEADER_REC + content_of_msg, "utf8"))


def handle_client(client,client_address):  # Takes client socket as argument.
    """Handles a single client connection."""
    while True:
        info_received = client.recv(BUFSIZ).decode("utf8").split('||')
        username_recieved = info_received[0]
        password_recieved = info_received[1]
        if  str(username_recieved).startswith(HEADER_SignUp) and str(password_recieved).startswith(HEADER_SignUp) :
             if  str(username_recieved.replace(HEADER_SignUp,"")) not in usernames.keys():
                    fullname_received = info_received[2]
                    passwords.append(password_recieved.replace(HEADER_SignUp,""))
                    fullnames.append(fullname_received.replace(HEADER_SignUp,""))
                    usernames[username_recieved.replace(HEADER_SignUp,"")] = list(zip(passwords,fullnames))[-1]
                    clients[client] = usernames
                    list_of_existing_usernames.append(username_recieved.replace(HEADER_SignUp,""))
                    client.send(bytes(HEADER_Start, "utf8"))
                    sendAndReceive(client, username_recieved.replace(HEADER_SignUp, ""))

             elif str(username_recieved.replace(HEADER_SignUp,"")) in  usernames.keys():
                 client.send(bytes(HEADER_already_exist,"utf8"))


        elif str(username_recieved).startswith(HEADER_SignIn) and str(password_recieved).startswith(HEADER_SignIn) :
            if (username_recieved.replace(HEADER_SignIn,"") not in usernames.keys()) or (password_recieved.replace(HEADER_SignIn,"") not in usernames[username_recieved.replace(HEADER_SignIn,"")][0]):
                client.send(bytes(HEADER_SignIn, "utf8"))
            else :
                client.send(bytes(HEADER_Start, "utf8"))
                sendAndReceive(client,username_recieved.replace(HEADER_SignIn,""))



if __name__ == "__main__":

    Server.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections,)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()

    Server.close()
