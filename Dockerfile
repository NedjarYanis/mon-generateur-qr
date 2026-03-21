FROM python:3.12-slim

# Installation des dépendances système nécessaires pour Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxss1 \
    libgbm1 \
    libasound2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On copie les requirements en premier pour gagner du temps au prochain build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le reste
COPY . .

# On expose le port 5000 (celui de ton app.py)
EXPOSE 5000

# Lancement avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]