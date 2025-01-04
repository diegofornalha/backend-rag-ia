#!/usr/bin/env python3
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime


def check_langchain():
    """Verifica detalhadamente a conexão com LangChain"""
    langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", "")
    langchain_endpoint = os.environ.get("LANGCHAIN_ENDPOINT", "")

    if not langchain_endpoint:
        return {
            "error": "LANGCHAIN_ENDPOINT não está definido",
            "url": None,
            "ok": False,
        }

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
        return {
            "status": response.getcode(),
            "url": health_url,
            "headers": dict(response.headers),
            "ok": True,
        }
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
            return {
                "status": response.getcode(),
                "url": langchain_endpoint,
                "headers": dict(response.headers),
                "ok": True,
            }
        except urllib.error.HTTPError as e2:
            return {
                "error": str(e2),
                "status": e2.code,
                "url": langchain_endpoint,
                "headers_sent": dict(req.headers),
                "ok": False,
            }
    except Exception as e:
        return {"error": str(e), "url": health_url, "ok": False}


def check_supabase():
    """Verifica detalhadamente a conexão com Supabase"""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")

    if not supabase_url:
        return {"error": "SUPABASE_URL não está definida", "url": None, "ok": False}

    # Adiciona endpoint válido para health check
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
        return {
            "status": response.getcode(),
            "url": health_url,
            "headers": dict(response.headers),
            "ok": True,
        }
    except urllib.error.HTTPError as e:
        return {
            "error": str(e),
            "status": e.code,
            "url": health_url,
            "headers_sent": dict(req.headers),
            "ok": False,
        }
    except Exception as e:
        return {"error": str(e), "url": health_url, "ok": False}


def check_dns():
    """Verifica configurações DNS"""
    try:
        with open("/etc/resolv.conf") as f:
            dns_config = f.read()
    except (FileNotFoundError, PermissionError) as e:
        dns_config = f"Could not read DNS config: {e}"

    return dns_config


def check_github_search():
    """Testa a Search API do GitHub"""
    github_token = os.environ.get("GITHUB_TOKEN", "")
    repo = "diegofornalha/backend-rag-ia"  # Seu repositório

    headers = {"Accept": "application/vnd.github.v3+json"}

    if github_token:
        headers["Authorization"] = f"token {github_token}"

    searches = {
        "issues": f"https://api.github.com/search/issues?q=repo:{repo}+is:issue",
        "code": f"https://api.github.com/search/code?q=repo:{repo}+language:python",
        "commits": f"https://api.github.com/search/commits?q=repo:{repo}",
        "repositories": "https://api.github.com/search/repositories?q=language:python+topic:langchain",
    }

    results = {}
    for search_type, url in searches.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())

            results[search_type] = {
                "total_count": data.get("total_count", 0),
                "status": response.getcode(),
                "ok": True,
                "rate_limit": {
                    "limit": response.headers.get("X-RateLimit-Limit"),
                    "remaining": response.headers.get("X-RateLimit-Remaining"),
                    "reset": response.headers.get("X-RateLimit-Reset"),
                },
            }
        except urllib.error.HTTPError as e:
            results[search_type] = {"error": str(e), "status": e.code, "ok": False}
        except Exception as e:
            results[search_type] = {"error": str(e), "ok": False}

    return results


def check_github():
    """Verifica detalhadamente a conexão com GitHub"""
    github_token = os.environ.get("GITHUB_TOKEN", "")

    headers = {"Accept": "application/vnd.github.v3+json"}

    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        # Verifica os limites de taxa
        req = urllib.request.Request(
            "https://api.github.com/rate_limit", headers=headers
        )
        response = urllib.request.urlopen(req)
        rate_limits = json.loads(response.read())

        # Adiciona resultados da Search API
        search_results = check_github_search()

        return {
            "status": response.getcode(),
            "ok": True,
            "rate_limits": {
                "core": rate_limits["resources"]["core"],
                "search": rate_limits["resources"]["search"],
                "graphql": rate_limits["resources"]["graphql"],
            },
            "authenticated": bool(github_token),
            "headers": dict(response.headers),
            "search_results": search_results,
        }
    except urllib.error.HTTPError as e:
        return {
            "error": str(e),
            "status": e.code,
            "ok": False,
            "headers_sent": dict(req.headers),
        }
    except Exception as e:
        return {"error": str(e), "ok": False}


def check_connectivity():
    """Verifica conectividade com serviços importantes"""
    services = {"render_api": "https://api.render.com"}

    results = {}
    for name, url in services.items():
        if url:
            try:
                code = urllib.request.urlopen(url).getcode()
                results[name] = {"status": code, "ok": code == 200}
            except Exception as e:
                results[name] = {"status": str(e), "ok": False}

    # Adiciona verificações detalhadas
    results["supabase"] = check_supabase()
    results["langchain"] = check_langchain()
    results["github"] = check_github()

    return results


def check_internal_network():
    """Verifica rede interna"""
    return {
        "hostname": socket.gethostname(),
        "internal_ip": socket.gethostbyname(socket.gethostname()),
        "render_internal": os.environ.get("RENDER_INTERNAL_HOSTNAME"),
        "render_external": os.environ.get("RENDER_EXTERNAL_HOSTNAME"),
    }


def main():
    """Função principal que executa todas as verificações"""
    checks = {
        "timestamp": datetime.now().isoformat(),
        "dns_config": check_dns(),
        "connectivity": check_connectivity(),
        "internal_network": check_internal_network(),
    }

    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
