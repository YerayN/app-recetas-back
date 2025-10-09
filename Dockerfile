# -------------------------------
# 📦 Imagen base ligera de Python
# -------------------------------
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# No buffer de salida y logs más limpios
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# -------------------------------
# 🧰 Dependencias del sistema
# -------------------------------
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 📦 Instalar dependencias Python
# -------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# -------------------------------
# 📁 Copiar el proyecto
# -------------------------------
COPY . .

# -------------------------------
# 🧹 Recolectar archivos estáticos
# -------------------------------
RUN python manage.py collectstatic --noinput

# -------------------------------
# 🚪 Exponer el puerto del servicio
# -------------------------------
EXPOSE 8000

# -------------------------------
# 🚀 Comando de inicio con Gunicorn
# -------------------------------
# ⬇️ Sustituye 'backend' por el nombre real de tu módulo WSGI
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["bash", "start.sh"]
