# Étape 1 : base image
FROM python:3.11-slim

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier les fichiers nécessaires
COPY requirements.txt .
COPY listener_webhook.py .

# Étape 4 : installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : exposer le port
EXPOSE 7000

# Étape 6 : démarrer gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7000", "listener_webhook:app"]
