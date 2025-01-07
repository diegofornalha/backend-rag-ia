FROM python:3.11-slim as builder

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias apenas para build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .
COPY pyproject.toml .
COPY poetry.lock .

# Criar e usar ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Segunda etapa - imagem final
FROM python:3.11-slim

# Criar usuário não-root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copiar ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY . .

# Ajustar permissões
RUN chown -R appuser:appgroup /app && \
    chmod -R g+w /app

# Mudar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "backend_rag_ia.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
