# Imagen base de Python
FROM python:3.12-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia el requirements.txt de la raíz
COPY requirements.txt .

# Instala dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código
COPY . .

# Expone el puerto (Railway usa $PORT)
EXPOSE 8000

# Ejecuta el script de inicio
CMD ["sh", "start.sh"]
