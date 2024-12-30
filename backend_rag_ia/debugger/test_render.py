import time
from datetime import datetime
from typing import Any

import requests
from rich.console import Console
from rich.table import Table

console = Console()


def log(message, level="info"):
    """Log colorido e formatado."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {"info": "white", "success": "green", "error": "red", "warning": "yellow"}
    console.print(f"[{colors[level]}][{timestamp}] {message}")


def check_connection(url: str) -> dict[str, Any]:
    """Verifica conectividade básica com a URL."""
    try:
        response = requests.get(url, timeout=10)
        return {
            "success": True,
            "status_code": response.status_code,
            "latency": response.elapsed.total_seconds(),
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Erro de conexão - Verifique se o serviço está online",
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout - Serviço muito lento ou não responde",
        }
    except Exception as e:
        return {"success": False, "error": f"Erro inesperado: {e!s}"}


def diagnose_problem(test_results: dict[str, Any]) -> str:
    """Analisa resultados e sugere soluções."""
    if not test_results["connection"]["success"]:
        if "Timeout" in test_results["connection"].get("error", ""):
            return """
🔍 Possíveis problemas:
1. Cold start do Render em andamento
2. Serviço não iniciou corretamente
3. Erro na configuração do Gunicorn

🛠️ Soluções:
1. Aguarde alguns minutos para o cold start
2. Verifique os logs do Render
3. Confirme as configurações no render.yaml"""

        return """
🔍 Possíveis problemas:
1. Deploy ainda não concluído
2. Erro no build
3. Serviço não está rodando

🛠️ Soluções:
1. Verifique o status do deploy no dashboard do Render
2. Confira os logs de build
3. Verifique se as variáveis de ambiente estão configuradas"""

    if test_results.get("health", {}).get("status_code") != 200:
        return """
🔍 Possíveis problemas:
1. Erro interno na aplicação
2. Problema com dependências
3. Erro na configuração do FastAPI

🛠️ Soluções:
1. Verifique os logs da aplicação
2. Confirme se todas as dependências estão no requirements.txt
3. Verifique a configuração do FastAPI e Gunicorn"""

    return "✅ Serviço está funcionando corretamente!"


def test_render_api():
    """Testa e diagnostica a API no Render."""
    BASE_URL = "https://backend-rag-ia.onrender.com"
    results = {
        "connection": {"success": False},
        "health": {"success": False},
        "endpoints": {"success": False},
    }

    # Teste de Conexão
    log("Testando conexão com o serviço...", "info")
    results["connection"] = check_connection(BASE_URL)

    if not results["connection"]["success"]:
        log(f"❌ Falha na conexão: {results['connection'].get('error')}", "error")
        diagnosis = diagnose_problem(results)
        log("\nDiagnóstico:", "warning")
        console.print(diagnosis)
        return results

    log(
        f"✅ Conexão estabelecida (latência: {results['connection']['latency']:.2f}s)",
        "success",
    )

    # Health Check
    log("\nTestando Health Check...", "info")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        results["health"] = {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
        }

        if results["health"]["success"]:
            log("✅ Health Check OK", "success")
        else:
            log(f"❌ Health Check falhou (status: {response.status_code})", "error")
    except Exception as e:
        results["health"] = {"success": False, "error": str(e)}
        log(f"❌ Erro no Health Check: {e!s}", "error")

    # Diagnóstico Final
    log("\nDiagnóstico Final:", "warning")
    diagnosis = diagnose_problem(results)
    console.print(diagnosis)

    # Sumário
    table = Table(title="Sumário dos Testes")
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Detalhes", style="green")

    table.add_row(
        "Conexão",
        "✅" if results["connection"]["success"] else "❌",
        f"Latência: {results['connection'].get('latency', 'N/A')}s",
    )

    table.add_row(
        "Health Check",
        "✅" if results["health"]["success"] else "❌",
        f"Status: {results['health'].get('status_code', 'N/A')}",
    )

    console.print("\n", table)

    return results


if __name__ == "__main__":
    log("🚀 Iniciando diagnóstico do deploy no Render...", "info")

    max_retries = 3
    for attempt in range(max_retries):
        if attempt > 0:
            wait_time = 10 * (attempt + 1)
            log(f"\nTentativa {attempt + 1} de {max_retries}...", "warning")
            log(f"Aguardando {wait_time} segundos para o cold start...", "info")
            time.sleep(wait_time)

        results = test_render_api()
        if results["connection"]["success"] and results["health"]["success"]:
            log("\n✨ Deploy verificado e funcionando!", "success")
            break
    else:
        log("\n❌ Deploy com problemas após todas as tentativas.", "error")
