# Utilise Python 3.12
FROM python:3.12-slim

# Installe Google Chrome et les dépendances système pour Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean

# Définit le dossier de travail
WORKDIR /app

# Copie les fichiers du projet
COPY . .

# Installe les bibliothèques Python
RUN pip install --no-cache-dir -r basic/requirements.txt

# Lance l'application avec Gunicorn (plus stable que le serveur de test)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "basic.app:app"]