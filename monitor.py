import time
import requests
import sys
from datetime import datetime

def print_progress_bar(current, total, width=50):
    """Imprime uma barra de progresso."""
    percent = float(current) * 100 / total
    arrow = '=' * int(percent/100 * width - 1) + '>'
    spaces = ' ' * (width - len(arrow))
    elapsed = time.strftime('%M:%S', time.gmtime(current))
    total_time = time.strftime('%M:%S', time.gmtime(total))
    sys.stdout.write(f'\rProgresso: [{arrow}{spaces}] {elapsed}/{total_time} ({percent:.1f}%)')
    sys.stdout.flush()

print("Monitorando status da API...")
start_time = time.time()
timeout = 300  # 5 minutos em segundos

# Espera 4 minutos e 45 segundos (285 segundos)
while time.time() - start_time < 285:
    current_time = time.time() - start_time
    print_progress_bar(current_time, timeout)
    time.sleep(1)

print("\n\nVerificando status final antes do timeout...")
try:
    response = requests.get("https://backend-rag-ia.onrender.com/api/v1/health")
    if response.ok:
        data = response.json()
        docs_count = data.get("documents_count", 0)
        print(f"✓ API Conectada - Documentos: {docs_count}")
        if docs_count > 0:
            print("\n✨ Documentos carregados com sucesso!")
            sys.exit(0)
        else:
            print("\n⚠️ API conectada mas sem documentos.")
    else:
        print("× API ainda indisponível...")
except Exception as e:
    print(f"× Erro ao verificar status: {str(e)}")

print("\n⚠️ Tempo limite de 5 minutos atingido.")
sys.exit(1) 