# Use a imagem base do Docker Hub
ARG BASE_IMAGE=fornalha/backend:latest
FROM ${BASE_IMAGE}

WORKDIR /app

# Copia o código da aplicação
COPY . .

# Expõe a porta
EXPOSE 10000

# Define as variáveis de ambiente
ENV HOST=0.0.0.0
ENV PORT=10000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"] 