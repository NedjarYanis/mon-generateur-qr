FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl libnss3 libgconf-2-4 libfontconfig1 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# On lance app:app car le fichier app.py est maintenant à la racine
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
