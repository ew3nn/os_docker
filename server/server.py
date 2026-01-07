import socket
import threading

# Configuration
HOST = '0.0.0.0'
PORT = 9999

def handle_client(client_socket, address):
    """Fonction exécutée dans un thread séparé pour chaque client"""
    print(f"[NOUVEAU] Connexion acceptée de {address}")
    
    connected = True
    while connected:
        try:
            # Réception des données (buffer de 1024 octets)
            msg = client_socket.recv(1024).decode('utf-8')
            
            if not msg: # Si le message est vide, le client s'est déconnecté
                break
                
            print(f"[{address}] a dit : {msg}")
            
            # Réponse au client (ACK)
            response = f"Bien reçu client {address} !"
            client_socket.send(response.encode('utf-8'))
            
        except ConnectionResetError:
            break

    client_socket.close()
    print(f"[DECONNEXION] {address} est parti.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5) # File d'attente max de 5
    
    print(f"[MARCHE] Le serveur écoute sur {HOST}:{PORT}")
    
    while True:
        # Cette ligne bloque jusqu'à ce qu'un client arrive
        client_sock, addr = server.accept()
        
        # On délègue la gestion de ce client à un thread pour ne pas bloquer la boucle
        thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        thread.start()
        print(f"[ACTIF] Nombre de clients connectés : {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
