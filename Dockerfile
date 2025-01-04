# Imagem base Python
FROM python:3.11-slim

# Criar usuário não-root
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser

# Criar e configurar diretório da aplicação
WORKDIR /app

# Criar ambiente virtual primeiro
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/venv"

# Copiar requirements primeiro para aproveitar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos
COPY . .

# Ajustar permissões
RUN chown -R appuser:appgroup /app && \
    chmod -R g+w /app

# Trocar para usuário não-root
USER appuser

# Expõe a porta
EXPOSE 10000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/ || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "backend_rag_ia.api.main:app", "--host", "0.0.0.0", "--port", "10000"]
