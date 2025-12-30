# Usar una imagen base de Python 3.12 ligera desde ECR Public para evitar límites de Docker Hub
FROM public.ecr.aws/docker/library/python:3.12-slim

# Evitar la generación de archivos .pyc y asegurar que los logs se muestren en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para ChromaDB y otras librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo de embeddings para evitar demoras en el primer arranque
# Aplicamos el bypass de SSL por si la red de build lo requiere
RUN python -c "from app.utils.ssl_patch import apply_ssl_bypass; apply_ssl_bypass(); from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')"

# Copiar el resto del código de la aplicación
COPY . .

# Asegurar que el directorio de datos existe y tiene permisos
RUN mkdir -p data/chroma_db

# Exponer el puerto en el que corre Uvicorn
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
