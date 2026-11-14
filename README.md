# Générateur de QR Code Pass & Boissons

<p align="center">
  <a href="https://nedjaryanis.github.io/mon-generateur-qr/"><img src="https://img.shields.io/badge/Web%20App-En%20Ligne-success?logo=githubpages&logoColor=white" alt="Live App" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/SQLite-WAL-003B57?logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Multi--Arch-2496ED?logo=docker&logoColor=white" alt="Docker" /></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-15%2F15%20passed-brightgreen?logo=pytest&logoColor=white" alt="Tests" /></a>
</p>

<br/>

Application web complète développée pour générer et synchroniser instantanément vos passes d'accès Basic-Fit (Pass Journée, Pass Semaine), recharges boissons Yanga et cartes portique adhérents (protocole dynamique GM2).

---

## 🌐 Accès Instantané (Sans aucune commande ni installation)

Vous n'avez **aucun besoin de lancer Python ni d'héberger en local** :

### 1. 🚀 Application Web en ligne (GitHub Pages / PWA Mobile)
Accessible 24h/24 depuis n'importe quel smartphone, tablette ou ordinateur :
👉 **[https://nedjaryanis.github.io/mon-generateur-qr/](https://nedjaryanis.github.io/mon-generateur-qr/)**

* **📱 Installation en 1 clic sur smartphone (PWA) :**
  * **Sur iPhone (Safari) :** Appuyez sur l'icône de partage ⎋ > *« Sur l'écran d'accueil »*.
  * **Sur Android (Chrome) :** Appuyez sur les 3 points ⋮ > *« Installer l'application »*.
* **⚡ Fonctionne 100% hors-ligne :** Même en sous-sol ou sans connexion internet dans la salle de sport grâce au Service Worker embarqué.
* **🔒 100% Privé :** Tous vos QR codes et historiques restent enregistrés localement sur votre appareil.

### 2. 📂 Google Drive / Fichier Autonome Unique
Le fichier portable **`mon-generateur-qr-standalone.html`** regroupe l'intégralité de l'application, du style et du moteur QR en un seul fichier indépendant :
* Ouvrez-le directement dans n'importe quel navigateur (double-clic).
* Disponible directement sur votre Google Drive pour un accès direct depuis votre téléphone ou drive partagé.

### 3. ☁️ Déploiement Cloud 1-Clic (Render)
Si vous souhaitez héberger le serveur backend Python Flask complet en ligne gratuitement :
* Cliquez sur **Deploy to Render** via le fichier `render.yaml` pour obtenir une instance HTTPS dédiée permanente 24h/24.

---

## ✨ Fonctionnalités Principales

- **Générateur Natif Ultra-Rapide** : Génération instantanée de QR codes haute résolution en PNG et Base64 Data URL, sans dépendance tierce obligatoire.
- **Pass Journée & Semaine** : Création en un clic avec coordonnées personnalisées ou générées aléatoirement.
- **Suivi des Boissons (Yanga)** : Gestion des passes boissons (code format `V000xxxxxx`), compteur de 2 essais décrémentable directement depuis l'interface.
- **Carte Adhérent Portique (GM2)** : Générateur de trames dynamiques `GM2:{carte}:BPZ:{timestamp}:95A5CAF2` avec horodatage temps réel.
- **Base de Données SQLite Sécurisée** : Persistance transactionnelle (mode WAL) remplaçant les fichiers JSON plats, avec migration automatique des anciens fichiers `visitor_log.json` et `used_qr_codes.json`.
- **API QR Code Intégrée** : Endpoint `/api/qr?data=...` pour servir des images QR en direct.
- **Support Docker Multi-Architecture** : Image Docker optimisée pour architecture `amd64` (Intel/AMD) et `arm64` (Apple Silicon Mac M1/M2/M3, Raspberry Pi, AWS Graviton).
- **Suite de Tests Complète** : 15 tests unitaires et d'intégration avec `pytest`.

---

## 📁 Structure du Projet

```text
.
├── public/                  # Application Web PWA autonome déployée sur GitHub Pages
│   ├── index.html           # Interface web mobile-first complète
│   ├── qrcode.min.js        # Moteur QR code purement client-side (offline)
│   ├── manifest.json        # Configuration PWA pour écran d'accueil mobile
│   ├── sw.js                # Service Worker pour fonctionnement 100% hors-ligne
│   └── icons/               # Icônes pour iOS et Android
├── mon-generateur-qr-standalone.html # Fichier unique autonome pour Google Drive / local
├── .github/workflows/       # Déploiement automatisé GitHub Actions vers GitHub Pages
│   └── deploy-pages.yml
├── render.yaml              # Configuration de déploiement Cloud 1-clic sur Render
├── app.py                   # Serveur Flask, gestion des routes, API et gestion d'erreurs
├── database.py              # Couche d'accès aux données SQLite, migrations et transactions
├── qr_service.py            # Moteur natif de génération de QR codes (Pillow + qrcode)
├── automation.py            # Logique d'automatisation et génération de passes de repli
├── mail_service.py          # Gestionnaire d'adresses email temporaires sécurisé
├── requirements.txt         # Dépendances Python (Flask, qrcode, pillow, gunicorn, etc.)
├── Dockerfile               # Image Docker multi-plateforme avec Chromium et Gunicorn
├── pytest.ini               # Configuration Pytest
├── tests/                   # Suite de tests unitaires et d'intégration
│   └── test_app.py
├── static/                  # Feuilles de style CSS, favicon et icônes tactiles
└── templates/               # Gabarits HTML Jinja2 Flask
```

---

## 🚀 Lancement Local avec Python (Optionnel)

Si vous souhaitez exécuter le serveur Python en local :

```bash
# 1. Cloner le dépôt
git clone https://github.com/NedjarYanis/mon-generateur-qr.git
cd mon-generateur-qr

# 2. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Sous Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer la suite de tests
pytest -v

# 5. Démarrer l'application Flask
python app.py
```
L'application est accessible sur : **[http://localhost:5000](http://localhost:5000)**

---

<div align="center">
  <sub>Développé et optimisé par Yanis Nedjar</sub>
</div>
