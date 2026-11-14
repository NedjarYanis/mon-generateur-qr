FROM python:3.12-slim

# Empêche Python d'écrire des fichiers .pyc et force l'affichage immédiat des logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Installation des dépendances système, de Chromium et de ChromeDriver (multi-architecture amd64 & arm64)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Optimisation du cache Docker : installation des dépendances Python en premier
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'intégralité du code source
COPY . .

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exposition du port applicatif
EXPOSE 5000

# Healthcheck natif pour orchestrateurs Docker / Kubernetes / Render
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Lancement sécurisé avec Gunicorn (multi-threads + timeout adapté aux traitements)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]