# Générateur de QR Code Pass & Boissons

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/SQLite-WAL-003B57?logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Multi--Arch-2496ED?logo=docker&logoColor=white" alt="Docker" /></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-15%2F15%20passed-brightgreen?logo=pytest&logoColor=white" alt="Tests" /></a>
  <a href="https://getbootstrap.com/"><img src="https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white" alt="Bootstrap" /></a>
</p>

<br/>

Application web complète développée avec **Python Flask**, intégrant la génération haute résolution native de QR codes, la synchronisation des passes journaliers et semaine, le suivi des recharges de boissons, la simulation de cartes adhérents (protocole portique GM2) et un stockage persistant thread-safe sous **SQLite**.

---

## ✨ Fonctionnalités

- **Générateur Natif Ultra-Rapide** : Génération instantanée de QR codes haute résolution en PNG et Base64 Data URL, sans dépendance tierce obligatoire.
- **Pass Journée & Semaine** : Création en un clic avec coordonnées personnalisées ou générées aléatoirement.
- **Suivi des Boissons (Yanga)** : Gestion des passes boissons (code format `V000xxxxxx`), compteur de 2 essais décrémentable et historique d'utilisation.
- **Carte Adhérent Portique (GM2)** : Générateur de trames dynamiques `GM2:{carte}:BPZ:{timestamp}:95A5CAF2` avec rendu direct en AJAX.
- **Base de Données SQLite Sécurisée** : Persistance transactionnelle (mode WAL) remplaçant les fichiers JSON plats, avec migration automatique des anciens fichiers `visitor_log.json` et `used_qr_codes.json`.
- **API QR Code Intégrée** : Endpoint `/api/qr?data=...` pour servir des images QR en direct.
- **Support Docker Multi-Architecture** : Image Docker optimisée pour architecture `amd64` (Intel/AMD) et `arm64` (Apple Silicon Mac M1/M2/M3, Raspberry Pi, AWS Graviton).
- **Suite de Tests Complète** : 15 tests unitaires et d'intégration avec `pytest`.

---

## 📁 Structure du Projet

```text
.
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
├── static/                  # Feuilles de style CSS, favicon et icônes tactiles PWA
└── templates/               # Gabarits HTML Jinja2 (index, qrAppGen, boissons, boissonNew)
```

---

## 🚀 Installation & Lancement

### Option 1 : En local avec Python

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

### Option 2 : Avec Docker (Recommandé en production)

```bash
# 1. Construire l'image Docker
docker build -t qr-pass-app .

# 2. Lancer le conteneur
docker run -d -p 5000:5000 --name qr-app qr-pass-app
```

---

## 🔌 API Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Page d'accueil & générateurs de passes |
| `POST` | `/result_day` | Génération de pass journée |
| `POST` | `/result_week` | Génération de pass semaine |
| `GET` | `/history` | Historique complet et filtrable des passes |
| `POST` | `/mark_used/<id>` | Marquer un pass comme utilisé et créditer 2 essais boissons |
| `GET` | `/boissons` | Tableau de bord des boissons disponibles et essais restants |
| `POST` | `/use_drink/<id>` | Consommer un essai boisson |
| `GET / POST` | `/get_boisson_image` | Génération d'un QR code boisson direct |
| `GET / POST` | `/app` & `/generate_app_qr` | Générateur de QR code carte club (format GM2) |
| `GET` | `/api/qr?data=<texte>` | Générateur d'image QR PNG en direct |
| `GET` | `/api/health` | Statut de santé pour orchestrateurs cloud |

---

## ⚙️ Variables d'Environnement (Optionnelles)

Créez un fichier `.env` si vous souhaitez personnaliser la configuration :

```env
PORT=5000
SECRET_KEY=votre_cle_secrete
DATABASE_PATH=passes.db
RAPIDAPI_KEY=votre_cle_si_disponible
ENABLE_SELENIUM=false
```

---

<div align="center">
  <sub>Développé et optimisé par Yanis Nedjar</sub>
</div>
