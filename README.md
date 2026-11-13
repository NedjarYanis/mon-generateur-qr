# G?n?rateur de QR Code Pass

<div align="center">
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![Selenium](https://img.shields.io/badge/Selenium-Headless-green?logo=selenium&logoColor=white)](https://www.selenium.dev/)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
  [![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
</div>

<br/>

Application web compl?te d?velopp?e avec **Python Flask** et automatis?e via **Selenium WebDriver**, permettant la g?n?ration, la gestion et la synchronisation de passes d'acc?s avec QR code dynamique. L'application est enti?rement conteneuris?e avec **Docker** pour un d?ploiement fiable en environnement cloud ou sur serveur d?di?.

---

## Fonctionnalit?s

- **Automatisation Headless** : Int?gration de Chrome Headless via Selenium pour la r?cup?ration dynamique de jetons et codes d'acc?s.
- **Interface Web Ergonomique** : Rendu responsive sous Bootstrap 5 avec barre de progression interactive et gestion des vues mobiles.
- **Support PWA / Mobile** : M?tadonn?es et ic?nes tactiles Apple (`apple-touch-icon`) configur?es pour un ajout direct sur ?cran d'accueil smartphone.
- **Conteneurisation Docker** : Environnement isol? int?grant Google Chrome, ChromeDriver et toutes les d?pendances Python pour une mise en production instantan?e.

---

## Structure du Projet

```text
.
??? app.py                   # Serveur Flask, logique de routage et pilote Selenium
??? requirements.txt         # D?pendances Python (Flask, selenium, requests, etc.)
??? Dockerfile               # Image Docker multi-plateforme avec Chrome headless
??? static/                  # Feuilles de style CSS, favicon et ic?nes d'application
??? templates/               # Gabarits HTML Jinja2 (index, qrAppGen, boissons)
```

---

## Installation & Lancement

### Option 1 : Avec Docker (Recommand?)

```bash
# 1. Construire l'image Docker
docker build -t qr-pass-app .

# 2. Lancer le conteneur sur le port 5000
docker run -d -p 5000:5000 --name qr-app qr-pass-app
```
L'application est disponible sur : **[http://localhost:5000](http://localhost:5000)**

### Option 2 : En local avec Python

```bash
# 1. Cloner le d?p?t
git clone https://github.com/NedjarYanis/mon-generateur-qr.git
cd mon-generateur-qr

# 2. Cr?er l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sous Windows : .env\Scripts\Activate.ps1

# 3. Installer les d?pendances
pip install -r requirements.txt

# 4. Lancer le serveur Flask
python app.py
```

---

<div align="center">
  <sub>D?velopp? par Yanis Nedjar</sub>
</div>
