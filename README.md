# Python-Apache-Deployment-Automation
Outil Python d’automatisation du déploiement local d’un site Apache. Le script contrôle le service (installé, actif, ou démarré), crée un virtual host complet (nexa.local), recharge la configuration, et notifie les résultats via ntfy.sh (IMPORTANT : Installer "ntfy" via Play Store ou App Store). Inclut un rapport JSON détaillant chaque étape du processus.


# Automatisation du déploiement Apache — Nexa Local Host Setup

Script Python pour automatiser la configuration d’un serveur **Apache** local avec un **virtual host `nexa.local`**.  
Le script vérifie l’installation et le statut du service, crée le virtual host, met à jour `/etc/hosts`, teste la disponibilité du site et envoie une notification via [ntfy.sh](https://ntfy.sh) pour signaler le résultat du déploiement.

---

## Fonctionnalités

- Vérifie si Apache est installé (`apache2` ou `httpd`)  
- Vérifie si Apache est en cours d’exécution  
- Démarre Apache si nécessaire  
- Crée un virtual host local `nexa.local` avec un index HTML simple  
- Ajoute `127.0.0.1 nexa.local` dans `/etc/hosts` si nécessaire  
- Teste la réponse HTTP du site  
- Envoie une notification **ntfy** avec le statut du déploiement  
- Génère un rapport JSON récapitulatif dans le terminal  

---

## Prérequis

- Python 3.x  
- Apache (`apache2` ou `httpd`) installé  
- Accès **sudo** sur le système  
- Connexion Internet pour la notification ntfy  

---

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/Mareme25/Python-Apache-Deployment-Automation.git
cd deployment.py 
```

## Installer les dépendances :
```bash 
pip install -r requirements.txt 
```

## Exécuter le script avec sudo (nécessaire pour modifier /etc/hosts et recharger Apache) :
``` bash 
sudo python3 deployment.py
```
Le script affichera un rapport JSON final indiquant l’état de chaque étape.

## Exemple de sortie
````
json
{
    "apache_installed": true,
    "apache_running": true,
    "apache_started": false,
    "virtual_host_created": true,
    "hosts_file_updated": false,
    "nexa_local_responding": true,
    "http_status_code": 200,
    "ntfy_notification_sent": true
}
````

## Auteur

Mareme NGONDI

Projet réalisé dans le cadre des cours à Nexa Digital School.
