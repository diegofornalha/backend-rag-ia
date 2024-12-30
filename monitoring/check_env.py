#!/usr/bin/env python3
import os
import sys
import json
import platform
from datetime import datetime


def check_python_env():
    """Verifica o ambiente Python"""
    return {
        "python_version": sys.version,
        "python_path": sys.executable,
        "pip_packages": os.popen("pip list --format=json").read(),
        "environment": os.environ.get("ENVIRONMENT"),
        "timestamp": datetime.now().isoformat(),
    }


def check_disk_space():
    """Verifica espaço em disco"""
    df = os.popen("df -h /").read()
    return {"disk_info": df, "timestamp": datetime.now().isoformat()}


def check_network():
    """Verifica conectividade de rede"""
    curl_render = os.popen(
        "curl -s -w '%{http_code}' -o /dev/null https://api.render.com"
    ).read()
    return {
        "render_api_status": curl_render,
        "dns_servers": open("/etc/resolv.conf").read(),
        "timestamp": datetime.now().isoformat(),
    }


def main():
    """Função principal que executa todas as verificações"""
    checks = {
        "environment": check_python_env(),
        "disk": check_disk_space(),
        "network": check_network(),
    }

    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
