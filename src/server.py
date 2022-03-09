import socket
from _thread import *
import pickle
import sys
from traceback import print_tb

# server ip address
server = "192.168.1.66"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

players = [0, 1]

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
                index = (player + 1) % 2
                reply = not (players[index] == index)
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
            players = [0, 1]

        start_new_thread(threaded_client, (conn, current_player))
        current_player += 1
    except KeyboardInterrupt:
        print("Ending program")
        break
        