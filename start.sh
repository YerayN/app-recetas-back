#!/usr/bin/env sh
set -e  # detiene el script si algo falla

python manage.py migrate --noinput
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'yeraynavarroyanini@gmail.com', 'Congo1234')" | python manage.py shell
gunicorn recetas_backend.wsgi:application --bind 0.0.0.0:$PORT

echo "🚀 Iniciando despliegue Django en producción..."

# 1️⃣ Asegurar que pip está actualizado
pip install --upgrade pip

# 2️⃣ Instalar dependencias
pip install -r requirements.txt

# 3️⃣ Aplicar migraciones de base de datos
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

# 4️⃣ Recolectar archivos estáticos (solo si no se hizo en build)
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# 5️⃣ Iniciar el servidor Gunicorn
echo "🔥 Iniciando Gunicorn..."
gunicorn recetas_backend.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --log-level info

