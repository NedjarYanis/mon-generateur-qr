# Générateur de QR Code Pass

<div align="center">
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![Selenium](https://img.shields.io/badge/Selenium-Headless-green?logo=selenium&logoColor=white)](https://www.selenium.dev/)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
  [![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
</div>

<br/>

Application web complète développée avec **Python Flask** et automatisée via **Selenium WebDriver**, permettant la génération, la gestion et la synchronisation de passes d'accès avec QR code dynamique. L'application est entièrement conteneurisée avec **Docker** pour un déploiement fiable en environnement cloud ou sur serveur dédié.

---

## Fonctionnalités

- **Automatisation Headless** : Intégration de Chrome Headless via Selenium pour la récupération dynamique de jetons et codes d'accès.
- **Interface Web Ergonomique** : Rendu responsive sous Bootstrap 5 avec barre de progression interactive et gestion des vues mobiles.
- **Support PWA / Mobile** : Métadonnées et icônes tactiles Apple (`apple-touch-icon`) configurées pour un ajout direct sur écran d'accueil smartphone.
- **Conteneurisation Docker** : Environnement isolé intégrant Google Chrome, ChromeDriver et toutes les dépendances Python pour une mise en production instantanée.

---

## Structure du Projet

```text
.
├── app.py                   # Serveur Flask, logique de routage et pilote Selenium
├── requirements.txt         # Dépendances Python (Flask, selenium, requests, etc.)
├── Dockerfile               # Image Docker multi-plateforme avec Chrome headless
├── static/                  # Feuilles de style CSS, favicon et icônes d'application
└── templates/               # Gabarits HTML Jinja2 (index, qrAppGen, boissons)
```

---

## Installation & Lancement

### Option 1 : Avec Docker (Recommandé)

```bash
# 1. Construire l'image Docker
docker build -t qr-pass-app .

# 2. Lancer le conteneur sur le port 5000
docker run -d -p 5000:5000 --name qr-app qr-pass-app
```
L'application est disponible sur : **[http://localhost:5000](http://localhost:5000)**

### Option 2 : En local avec Python

```bash
# 1. Cloner le dépôt
git clone https://github.com/NedjarYanis/mon-generateur-qr.git
cd mon-generateur-qr

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sous Windows : .\venv\Scripts\Activate.ps1

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur Flask
python app.py
```

---

<div align="center">
  <sub>Développé par Yanis Nedjar</sub>
</div>
