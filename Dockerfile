# Estágio de construção
FROM python:3.11-slim as builder

WORKDIR /app

# Instala dependências essenciais para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    swig \
    git \
    cmake \
    pkg-config \
    libopenblas-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria e ativa o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências Python em camadas para melhor cache
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -U pip setuptools wheel

# Instala primeiro as dependências base
RUN . /opt/venv/bin/activate && pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-dotenv==1.0.0 \
    gunicorn>=22.0.0 \
    pydantic==2.5.2 \
    "httpx>=0.24.0,<0.26.0"

# Instala huggingface-hub primeiro com versão compatível
RUN . /opt/venv/bin/activate && pip install --no-cache-dir huggingface-hub==0.17.3

# Instala numpy primeiro
RUN . /opt/venv/bin/activate && pip install --no-cache-dir numpy

# Clona e compila o faiss para ARM64
RUN git clone https://github.com/facebookresearch/faiss.git && \
    cd faiss && \
    cmake -B build . -DFAISS_ENABLE_GPU=OFF -DFAISS_ENABLE_PYTHON=ON \
    -DFAISS_OPT_LEVEL=generic -DBUILD_TESTING=OFF \
    -DPython_EXECUTABLE=$(which python) && \
    make -C build -j$(nproc) && \
    cd build/faiss/python && \
    python setup.py install

# Instala as dependências ML que são mais pesadas
RUN . /opt/venv/bin/activate && pip install --no-cache-dir \
    "torch==2.2.0" \
    "transformers==4.35.0" \
    "sentence-transformers==2.2.2"

# Por fim, instala o resto das dependências
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Estágio final
FROM python:3.11-slim

WORKDIR /app

# Copia o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código da aplicação
COPY . .

# Expõe a porta
EXPOSE 10000

# Define as variáveis de ambiente
ENV HOST=0.0.0.0
ENV PORT=10000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"] 