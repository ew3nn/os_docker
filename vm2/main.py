import socket
import os
import threading
import time
import random

MY_NAME = os.getenv('MY_NAME')
LISTEN_PORT = 5000

# L'ANNUAIRE : On récupère les adresses des copains depuis le docker-compose
# Le format attendu dans les variables est "host:port"
PEERS = {
    "c1": os.getenv('ADDR_C1'),
    "c2": os.getenv('ADDR_C2'),
    "c3": os.getenv('ADDR_C3'),
    "c4": os.getenv('ADDR_C4')
}

# 1. Partie SERVEUR (Écoute)
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(5)
    print(f"[{MY_NAME}] 🟢 Serveur démarré sur le port {LISTEN_PORT}")
    
    while True:
        try:
            client_sock, addr = server.accept()
            message = client_sock.recv(1024).decode('utf-8')
            print(f"[{MY_NAME}] 📩 REÇU : {message}")
            client_sock.close()
        except Exception as e:
            print(f"Erreur réception: {e}")

# 2. Partie CLIENT (Envoi)
def send_message(target_name, msg):
    address_string = PEERS.get(target_name)
    
    if not address_string:
        print(f"[{MY_NAME}] ❌ Impossible de trouver l'adresse de {target_name}")
        return

    # On ignore l'envoi vers soi-même
    if target_name == MY_NAME:
        return

    try:
        host, port = address_string.split(':')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        full_message = f"De {MY_NAME} pour {target_name} : {msg}"
        s.send(full_message.encode('utf-8'))
        s.close()
        print(f"[{MY_NAME}] ENVOYÉ vers {target_name} ({host}:{port})")
    except Exception as e:
        print(f"[{MY_NAME}] Échec vers {target_name} : {e}")

# Lancement du serveur en arrière-plan
threading.Thread(target=start_server).start()

# Attente que tout le monde démarreezj
time.sleep(5)

# 3. Simulation : On envoie un message à quelqu'un au hasard toutes les 5s
while True:
    time.sleep(5)
    # Choisir un copain au hasard qui n'est pas moi
    possibles = [p for p in PEERS.keys() if p != MY_NAME]
    destinataire = random.choice(possibles)
    
    send_message(destinataire, "Salut, ça va ?")
