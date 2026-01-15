# README - Projet P2P (VM2)

Ce dossier contient la configuration pour la **VM2**. Cette machine héberge deux instances de l'application de jeu, mais aussi le **Registre Docker** nécessaire pour distribuer l'image à la VM1.

## Description des Conteneurs
Cette machine fait tourner 3 services principaux via Docker :

### 1. Le Registry (`registry:2`)
* **Rôle :** Sert de dépôt central pour les images Docker.
* **Fonctionnement :** Il écoute sur le port `6000`. C'est ici que l'image de l'application (`mon-app-socket`) est stockée. La VM1 viendra pull l'image depuis ce service pour s'assurer que tout le monde utilise exactement la même version du code.

### 2. Les Conteneurs de Jeu (`c3` et `c4`)
Ces conteneurs exécutent le script Python `main.py` et simulent des pairs (peers) dans le réseau P2P.
* **Serveur Public :** Chaque conteneur écoute sur le port 5000 interne (mappé sur `5003` pour c3 et `5004` pour c4 sur la machine hôte) pour recevoir des messages publics ou des invitations.
* **Logique P2P :**
* Ils tentent de se connecter aux autres pairs (`c1`, `c2`, etc.) via les adresses IP définies dans le `docker-compose.yml`.
* Ils envoient aléatoirement des messages (affichage du score) ou des invitations de jeu.
* **Le Jeu :** En cas d'invitation acceptée, une connexion socket directe (privée) est établie sur une plage de ports dynamique (ex: 5300-5310) pour jouer à Pierre-Feuille-Ciseaux.


## Lancement et Compilation
```bash
docker-compose up -d --build
```
Cela va démarrer le registre et lancer les conteneurs `c3` et `c4`.

## Vérification
**Vérifier les logs du jeu :**
Pour voir si `c3` discute ou joue :
```bash
docker logs -f c3

```

## ⚠️ Notes Réseau
Les adresses IP des pairs distants (`ADDR_C1`, `ADDR_C2`) et les ports sont codés en dur dans le fichier docker-compose.
Nous aurions bien aimé rendre la découverte de nouveaux joueurs automatiques mais nous avons pas eu le temps de l'implémanter