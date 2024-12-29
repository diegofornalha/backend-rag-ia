import requests
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_render_api():
    BASE_URL = "https://oraculo-api-latest.onrender.com"
    
    # Teste 1: Health Check
    log("Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            log("✅ Health Check OK")
            log(f"Resposta: {response.json()}")
        else:
            log(f"❌ Health Check falhou. Status: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erro no Health Check: {str(e)}")
        return False

    # Aguarda um pouco antes do próximo teste
    time.sleep(2)

    # Teste 2: Chat Endpoint
    log("\nTestando Chat Endpoint...")
    try:
        test_message = "Olá, isso é um teste de conectividade. Por favor, responda com uma mensagem curta."
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": test_message}
        )
        
        if response.status_code == 200:
            log("✅ Chat Endpoint OK")
            log(f"Mensagem enviada: {test_message}")
            log(f"Resposta recebida: {response.json()['response']}")
        else:
            log(f"❌ Chat Endpoint falhou. Status: {response.status_code}")
            log(f"Resposta de erro: {response.text}")
            return False
    except Exception as e:
        log(f"❌ Erro no Chat Endpoint: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    log("Iniciando testes da API no Render...")
    
    # Tenta algumas vezes devido ao cold start
    max_retries = 3
    for attempt in range(max_retries):
        if attempt > 0:
            wait_time = 10 * (attempt + 1)  # Aumenta o tempo de espera a cada tentativa
            log(f"\nTentativa {attempt + 1} de {max_retries}...")
            log(f"Aguardando {wait_time} segundos para o cold start...")
            time.sleep(wait_time)
            
        if test_render_api():
            log("\n✅ Todos os testes passaram!")
            break
    else:
        log("\n❌ Os testes falharam após todas as tentativas.") 