# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Recolectar archivos estáticos de Django
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command
CMD ["bash", "start.sh"]
