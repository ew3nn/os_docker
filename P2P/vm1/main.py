import socket
import os
import threading
import time
import random
import json

MY_NAME = os.getenv('MY_NAME', 'Unknown')
victoty = 0
defeat = 0

# On récupère le port public et la plage privée
PUBLIC_PORT = int(os.getenv('MY_PUBLIC_PORT', 5000))
start_range = int(os.getenv('PRIVATE_RANGE_START', 5001))
PRIVATE_PORT_RANGE = range(start_range, start_range + 10)

PEERS = {
    "c1": os.getenv('ADDR_C1'),
    "c2": os.getenv('ADDR_C2'),
    "c3": os.getenv('ADDR_C3'),
    "c4": os.getenv('ADDR_C4')
}

def paper_rock_scissors(conn):
    global victoty, defeat
    txt_game = """--- Bienvenue au jeu Pierre-Feuille-Ciseaux ! ---"""
    my_choice = random.choice(['rock', 'paper', 'scissors'])
    opponent_choice = conn.recv(1024).decode('utf-8')
    txt_game += f"\n{MY_NAME} joue : {my_choice}"
    txt_game += f"\nAdversaire joue : {opponent_choice}"
    if opponent_choice == my_choice:
        txt_game += "\nÉgalité !"
    elif (my_choice == 'rock' and opponent_choice == 'scissors') or (my_choice == 'scissors' and opponent_choice == 'paper') or (my_choice == 'paper' and opponent_choice == 'rock'):
        victoty += 1
        txt_game += f"{MY_NAME} a gagné !"
    else:
        defeat += 1
        txt_game += f"\n{MY_NAME} a perdu !"
    conn.send(txt_game.encode('utf-8'))
    print(txt_game)

def get_peer_ip(peer_name):
    addr = PEERS.get(peer_name)
    if addr:
        return addr.split(':')[0]
    return None

def find_free_port():
    for port in PRIVATE_PORT_RANGE:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port
    return None

def start_private_host(port, target_name):
    print(f"[{MY_NAME}] salon privé sur le port {port} pour {target_name}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    server.settimeout(10)
    try:
        conn, addr = server.accept()
        print(f"[{MY_NAME}] - {target_name} a rejoint le salon privé :)")
        paper_rock_scissors(conn)
        conn.close()
    except socket.timeout:
        print(f"[{MY_NAME}] - {target_name} n'a pas rejoint :(")
    finally:
        server.close()

def join_private_chat(host_ip, port, target_name):
    print(f"[{MY_NAME}] - rejoins le salon privé de {target_name}")
    time.sleep(1)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host_ip, port))
        my_choice = random.choice(['rock', 'paper', 'scissors'])
        s.send(f"{my_choice}".encode('utf-8'))
        result = s.recv(1024).decode('utf-8')
        print(result)
        s.send(f"[{MY_NAME}] - gg".encode('utf-8'))
        s.close()
    except Exception as e:
        print(f"[{MY_NAME}] - Impossible de rejoindre le privé : {e}")

def handle_client(conn):
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data: return
        message = json.loads(data)
        sender = message.get('from')
        msg_type = message.get('type')
        if msg_type == "PUBLIC_MSG":
            print(f"[{MY_NAME}] - (Public) {sender}: {message['content']}")
        elif msg_type == "INVITE":
            print(f"[{MY_NAME}] - invit de {sender}")
            host_ip = get_peer_ip(sender)
            if host_ip:
                threading.Thread(target=join_private_chat, args=(host_ip, message['port'])).start()

    except Exception as e:
        print(f"[{MY_NAME}] - Erreur lecture JSON: {e}")
    finally:
        conn.close()

def start_public_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PUBLIC_PORT)) 
    server.listen(5)
    print(f"[{MY_NAME}] - Lobby Public ouvert sur {PUBLIC_PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()


def send_public_packet(target_name, packet_dict):
    addr_str = PEERS.get(target_name)
    if not addr_str or target_name == MY_NAME: return
    try:
        host, port = addr_str.split(':')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.send(json.dumps(packet_dict).encode('utf-8'))
        s.close()
    except Exception as e:
        pass

def loop():
    while True:
        time.sleep(random.randint(3, 8))
        possibles = [p for p in PEERS.keys() if p != MY_NAME]
        target = random.choice(possibles)
        action = random.choice(["TALK", "TALK", "INVITE"])
        if action == "TALK":
            msg = {
                "type": "PUBLIC_MSG",
                "from": MY_NAME,
                "content": f"J'ai {victoty} victoires pour {defeat} défaites, ce qui fait un winrate de {victoty/(defeat+1):.2f} !"
            }
            for peer in possibles:
                send_public_packet(peer, msg)

        elif action == "INVITE":
            private_port = find_free_port()
            if private_port:
                invite_msg = {
                    "type": "INVITE",
                    "from": MY_NAME,
                    "port": private_port
                }
                threading.Thread(target=start_private_host, args=(private_port, target)).start()
                send_public_packet(target, invite_msg)
                print(f"[{MY_NAME}] - invit envoyée à {target}")

if __name__ == "__main__":
    threading.Thread(target=start_public_server).start()    
    time.sleep(5)
    loop()
