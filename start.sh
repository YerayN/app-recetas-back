#!/usr/bin/env sh
set -e  # detiene el script si algo falla

# Instalar dependencias desde el archivo local
pip install --upgrade pip
pip install -r requirements.txt

# Aplicar migraciones y recopilar estáticos
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Iniciar el servidor con Gunicorn
gunicorn recetas_backend.wsgi:application --bind 0.0.0.0:$PORT
