FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-pyaudio \
    libopencv-dev \
    python3-opencv \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    festival* \
    festvox-kallpc16k \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt requirements-dev.txt ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p logs data/uploads data/exports static/uploads

# Permissions
RUN chmod +x scripts/*.py

# Exposer le port
EXPOSE 8000

# Variables d'environnement par défaut
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
