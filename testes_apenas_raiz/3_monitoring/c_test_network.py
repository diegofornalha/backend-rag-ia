import json
import os
import socket
import urllib.error
import urllib.request

import pytest


def test_langchain_connection(check_env_vars):
    """Testa a conexão com LangChain"""
    langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", "")
    langchain_endpoint = os.environ.get("LANGCHAIN_ENDPOINT", "")

    if not langchain_endpoint:
        pytest.skip("LANGCHAIN_ENDPOINT não está definido")

    # Endpoint para verificação de status da API
    health_url = f"{langchain_endpoint}/health"

    try:
        req = urllib.request.Request(
            health_url,
            headers={
                "Authorization": f"Bearer {langchain_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        response = urllib.request.urlopen(req)
        assert response.getcode() == 200, "Health check falhou"
    except urllib.error.HTTPError:
        # Se o health check falhar, tenta o endpoint principal
        try:
            req = urllib.request.Request(
                langchain_endpoint,
                headers={
                    "Authorization": f"Bearer {langchain_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            response = urllib.request.urlopen(req)
            assert response.getcode() == 200, "Endpoint principal falhou"
        except Exception as e:
            pytest.fail(f"Erro ao conectar com LangChain: {e}")


def test_supabase_connection(check_env_vars):
    """Testa a conexão com Supabase"""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")

    if not supabase_url:
        pytest.skip("SUPABASE_URL não está definida")

    health_url = f"{supabase_url}/rest/v1/"

    try:
        req = urllib.request.Request(
            health_url,
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "apikey": supabase_key,
                "Accept": "application/json",
            },
        )
        response = urllib.request.urlopen(req)
        assert response.getcode() == 200, "Conexão com Supabase falhou"
    except Exception as e:
        pytest.fail(f"Erro ao conectar com Supabase: {e}")


def test_github_api(check_env_vars):
    """Testa a conexão com GitHub API"""
    github_token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}

    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        req = urllib.request.Request(
            "https://api.github.com/rate_limit", headers=headers
        )
        response = urllib.request.urlopen(req)
        assert response.getcode() == 200, "Conexão com GitHub API falhou"

        rate_limits = json.loads(response.read())
        assert "resources" in rate_limits, "Resposta da API inválida"
        assert "core" in rate_limits["resources"], "Limite de taxa não encontrado"
    except Exception as e:
        pytest.fail(f"Erro ao conectar com GitHub API: {e}")


def test_render_api():
    """Testa a conexão com Render API"""
    try:
        response = urllib.request.urlopen("https://api.render.com")
        assert response.getcode() == 200, "Conexão com Render API falhou"
    except Exception as e:
        pytest.fail(f"Erro ao conectar com Render API: {e}")


def test_internal_network():
    """Testa configurações de rede interna"""
    hostname = socket.gethostname()
    assert hostname, "Hostname não encontrado"

    try:
        internal_ip = socket.gethostbyname(hostname)
        assert internal_ip, "IP interno não encontrado"
    except Exception as e:
        pytest.fail(f"Erro ao verificar rede interna: {e}")

    # Verifica variáveis do Render se estiver no ambiente de produção
    if os.environ.get("RENDER_INTERNAL_HOSTNAME"):
        assert os.environ.get("RENDER_EXTERNAL_HOSTNAME"), "Hostname externo do Render não encontrado" 