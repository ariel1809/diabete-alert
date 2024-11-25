# Utilisez une image Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /diabete-alerte

# Copier les fichiers nécessaires
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:diabate-alerte"]