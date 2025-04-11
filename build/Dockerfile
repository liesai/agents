# Utilise une image Python légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copie les fichiers requis
COPY . /app

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Port utilisé par Flask
EXPOSE 5000

# Commande de lancement
CMD ["python", "listener_webhook.py"]
