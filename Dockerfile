# Utilisez une image Python légère
FROM python:3.10-slim

# Installer les dépendances système (si nécessaire)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /diabete-alerte

# Copier uniquement les fichiers nécessaires
COPY . .

# Installer les dépendances Python
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Créer un utilisateur non-root pour exécuter l’application
RUN useradd -m appuser
USER appuser

# Exposer le port (optionnel)
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]