# Dockerfile para Leitor Inteligente - Baseado em originacao-pipeline
# Padrão walterrosa2: Python 3.12-bullseye

FROM python:3.12-bullseye

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Diretório de trabalho
WORKDIR /app

# Instala dependências de sistema (necessárias para processamento de PDF/Imagens se houver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Expõe as portas internas (Docker Compose fará o mapeamento externo)
EXPOSE 8513 8514

# O comando padrão será o start, mas o docker-compose irá sobrescrever
CMD ["python"]
