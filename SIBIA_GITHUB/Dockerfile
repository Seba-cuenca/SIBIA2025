# Dockerfile para SIBIA desplegado desde subcarpeta SIBIA_GITHUB
# Optimizado para Google Cloud Run

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    HOST=0.0.0.0 \
    DEBUG=false

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements específicos de la subcarpeta
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo el contenido de SIBIA_GITHUB
COPY . .

RUN mkdir -p ml_training_data models logs reportes

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 600 --access-logfile - --error-logfile - --log-level info app_CORREGIDO_OK_FINAL:app
