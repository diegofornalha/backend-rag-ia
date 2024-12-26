FROM python:3.9-slim

WORKDIR /app

COPY test_render.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "test_render.py"] 