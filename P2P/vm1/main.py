import socket
import os
import threading
import time
import random
import json

MY_NAME = os.getenv('MY_NAME', 'Unknown')

# --- MODIFICATION ICI ---
# On récupère le port public depuis la config, sinon 5000 par défaut
PUBLIC_PORT = int(os.getenv('MY_PUBLIC_PORT', 5000))

# On récupère le début de la plage privée, sinon 5001 par défaut
start_range = int(os.getenv('PRIVATE_RANGE_START', 5001))
# On définit la plage (ex: de 5100 à 5110)
PRIVATE_PORT_RANGE = range(start_range, start_range + 10)

# L'ANNUAIRE (IP:Port)
PEERS = {
    "c1": os.getenv('ADDR_C1'),
    "c2": os.getenv('ADDR_C2'),
    "c3": os.getenv('ADDR_C3'),
    "c4": os.getenv('ADDR_C4')
}

# --- OUTILS RÉSEAU ---

def get_peer_ip(peer_name):
    """Extrait juste l'IP de la string 'host:port'"""
    addr = PEERS.get(peer_name)
    if addr:
        return addr.split(':')[0]
    return None

def find_free_port():
    """Cherche un port libre dans la plage 5001-5010"""
    for port in PRIVATE_PORT_RANGE:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port
    return None

# --- PARTIE 1 : LE CHAT PRIVÉ (Éphémère) ---

def start_private_host(port, target_name):
    """Je suis l'hôte du salon privé"""
    print(f"[{MY_NAME}] 🔒 Création salon privé sur le port {port} pour {target_name}")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    
    # On attend que l'invité se connecte (timeout 10s)
    server.settimeout(10)
    try:
        conn, addr = server.accept()
        print(f"[{MY_NAME}] 🤝 {target_name} a rejoint le salon privé !")
        
        # Discussion privée simple
        conn.send(f"Salut je vends du lsd tu en veux ? {target_name} !".encode('utf-8'))
        response = conn.recv(1024).decode('utf-8')
        print(f"[{MY_NAME}] 🔒 (Privé) Reçu : {response}")
        
        conn.close()
    except socket.timeout:
        print(f"[{MY_NAME}] 😢 {target_name} n'est pas venu...")
    finally:
        server.close()

def join_private_chat(host_ip, port):
    """Je rejoins un salon privé auquel on m'a invité"""
    print(f"[{MY_NAME}] 🏃 Je cours rejoindre le salon privé sur {host_ip}:{port}")
    time.sleep(1) # Petit délai pour être sûr que le serveur est prêt
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host_ip, port))
        
        msg = s.recv(1024).decode('utf-8')
        print(f"[{MY_NAME}] 🔒 (Privé) L'hôte dit : {msg}")
        
        s.send(f"[{MY_NAME}] Merci pour l'invit, c'est super calme ici.".encode('utf-8'))
        s.close()
    except Exception as e:
        print(f"[{MY_NAME}] ❌ Impossible de rejoindre le privé : {e}")

# --- PARTIE 2 : LE CHAT PUBLIC (Lobby 5000) ---

def handle_client(conn):
    """Gère un message reçu sur le port 5000"""
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data: return
        
        # On décode le JSON
        message = json.loads(data)
        sender = message.get('from')
        msg_type = message.get('type')

        if msg_type == "PUBLIC_MSG":
            print(f"[{MY_NAME}] 📢 (Public) {sender}: {message['content']}")
            
        elif msg_type == "INVITE":
            print(f"[{MY_NAME}] 📩 INVITATION REÇUE de {sender} pour le port {message['port']}")
            # On récupère l'IP de celui qui m'invite
            host_ip = get_peer_ip(sender)
            if host_ip:
                # On lance un thread pour rejoindre le privé (pour ne pas bloquer le public)
                threading.Thread(target=join_private_chat, args=(host_ip, message['port'])).start()

    except Exception as e:
        print(f"Erreur lecture JSON: {e}")
    finally:
        conn.close()

def start_public_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Utilise la variable PUBLIC_PORT au lieu de 5000 en dur
    server.bind(('0.0.0.0', PUBLIC_PORT)) 
    server.listen(5)
    print(f"[{MY_NAME}] 🟢 Lobby Public ouvert sur {PUBLIC_PORT}")
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()

# --- PARTIE 3 : L'ENVOYEUR (Simulation) ---

def send_public_packet(target_name, packet_dict):
    addr_str = PEERS.get(target_name)
    if not addr_str or target_name == MY_NAME: return

    try:
        host, port = addr_str.split(':')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        # On transforme le dictionnaire en JSON string
        s.send(json.dumps(packet_dict).encode('utf-8'))
        s.close()
    except Exception as e:
        # print(f"Echec envoi vers {target_name}") # Spam log off
        pass

def simulation_loop():
    while True:
        time.sleep(random.randint(3, 8))
        
        # Choix d'une cible au hasard
        possibles = [p for p in PEERS.keys() if p != MY_NAME]
        target = random.choice(possibles)
        
        # 1 chance sur 3 de lancer une INVITATION PRIVÉE
        action = random.choice(["TALK", "TALK", "INVITE"])
        
        if action == "TALK":
            msg = {
                "type": "PUBLIC_MSG",
                "from": MY_NAME,
                "content": "Salut tout le monde !"
            }
            send_public_packet(target, msg)
            print(f"[{MY_NAME}] 🗣️  Dit bonjour à {target} (Public)")
            
        elif action == "INVITE":
            # 1. Trouver un port libre
            private_port = find_free_port()
            if private_port:
                # 2. Préparer l'invitation
                invite_msg = {
                    "type": "INVITE",
                    "from": MY_NAME,
                    "port": private_port
                }
                # 3. Lancer mon serveur privé AVANT d'envoyer l'invit
                threading.Thread(target=start_private_host, args=(private_port, target)).start()
                
                # 4. Envoyer l'invit sur le canal public
                send_public_packet(target, invite_msg)
                print(f"[{MY_NAME}] 🎫 Invitation envoyée à {target} sur port {private_port}")

# --- DÉMARRAGE ---

if __name__ == "__main__":
    # 1. Lancer le serveur public
    threading.Thread(target=start_public_server).start()
    
    # 2. Attendre que les autres VMs démarrent
    time.sleep(5)
    
    # 3. Lancer la simulation d'actions
    simulation_loop()
