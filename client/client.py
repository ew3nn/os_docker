import socket
import time
import os
import random

# On récupère l'IP cible via une variable d'env, ou localhost par défaut
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT = 9999
MY_ID = os.getenv('CLIENT_ID', 'Inconnu')

def start_client():
    print(f"Tentative de connexion à {SERVER_IP}:{PORT}...")
    
    # Création de la socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, PORT))
        print(f"Connecté au serveur !")
        
        counter = 0
        while True:
            msg = f"Message {counter} de {MY_ID}"
            client.send(msg.encode('utf-8'))
            
            # Attente de la réponse
            reponse = client.recv(1024).decode('utf-8')
            print(f"Serveur a répondu : {reponse}")
            
            counter += 1
            time.sleep(3) # Pause de 3 secondes
            
    except Exception as e:
        print(f"Erreur ou déconnexion : {e}")
        client.close()

if __name__ == "__main__":
    # Petit délai aléatoire au démarrage pour ne pas que les 3 se connectent à la milliseconde près
    time.sleep(random.randint(1, 5)) 
    start_client()
