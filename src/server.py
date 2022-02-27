import socket
from _thread import *
import pickle
import sys
from traceback import print_tb

server = "192.168.1.115"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

players = ["P", "O"]

def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))

    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))

            if not data:
                print("Disconnected")
                break
            elif data == "connected":
                reply = not (player == 0 and players[1] == "O" or player == 1 and players[0] == "P")
            else:
                players[player] = data
                reply = players[0] if player == 1 else players[1]
            
            conn.sendall(pickle.dumps(reply))
        except:
            break
    
    print("Lost connection")
    conn.close()

current_player = 0

while True:
    try:
        conn, addr = s.accept()
        print("Connected to:", addr)
        
        # game test reset
        if current_player == 2:
            print("reset happen")
            current_player = 0
            players = ["P", "O"]

        start_new_thread(threaded_client, (conn, current_player))
        current_player += 1
    except KeyboardInterrupt:
        print("Ending program")
        break
        