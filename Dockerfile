# Usar imagen oficial de Python ligera
FROM python:3.11-slim

# Metadatos del proyecto
LABEL maintainer="Crypto Mining Simulator"
LABEL description="Simulador de Minería de Criptomonedas para Casa Grande, Perú en Streamlit"

# Variables de entorno para Python y Streamlit
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8506 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema mínimas requeridas para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY . /app

# Crear usuario no privilegiado para mayor seguridad
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Exponer el puerto configurado de Streamlit
EXPOSE 8506

# Healthcheck para verificar el estado de la aplicación
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8506/_stcore/health || exit 1

# Comando de inicio del servidor Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8506", "--server.address=0.0.0.0"]
