# Imagem base Python
FROM python:3.11-slim

# Criar usuário não-root
RUN useradd -m -U appuser

# Criar e configurar diretório da aplicação
WORKDIR /app
COPY . .

# Criar e ativar ambiente virtual
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Instalar dependências no ambiente virtual
RUN pip install --no-cache-dir -r requirements.txt

# Mudar permissões
RUN chown -R appuser:appuser /app

# Trocar para usuário não-root
USER appuser

# Expõe a porta
EXPOSE 10000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/ || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "backend_rag_ia.api.main:app", "--host", "0.0.0.0", "--port", "10000"]
