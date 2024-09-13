FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clonar o repositório
RUN git clone https://github.com/Andersonmathema/bsed.git .

# Instalar dependências
RUN pip3 install -r requirements.txt

# Copiar o arquivo postgres.py para o diretório de trabalho
COPY postgres.py .

# Executar o script postgres.py
CMD ["python3", "/app/postgres.py"]

