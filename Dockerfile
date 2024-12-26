FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Copia os arquivos essenciais primeiro
COPY requirements.txt .
COPY knowledge_base.csv .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto dos arquivos
COPY . .

EXPOSE ${PORT:-3000}

CMD ["sh", "-c", "uvicorn oracle:app --host 0.0.0.0 --port ${PORT:-3000} --workers 4"] 