#!/usr/bin/env python3
import os
import json
import pkg_resources
from datetime import datetime


def check_installed_packages():
    """Verifica pacotes instalados e suas versões"""
    packages = []
    for pkg in pkg_resources.working_set:
        packages.append(
            {"name": pkg.key, "version": pkg.version, "location": pkg.location}
        )
    return packages


def check_requirements():
    """Verifica requirements.txt se existir"""
    req_file = "/app/requirements.txt"
    if os.path.exists(req_file):
        with open(req_file) as f:
            return f.read()
    return "Requirements file not found"


def check_venv():
    """Verifica ambiente virtual"""
    return {
        "venv_path": os.environ.get("VIRTUAL_ENV"),
        "python_path": os.environ.get("PYTHONPATH"),
        "python_home": os.environ.get("PYTHONHOME"),
    }


def main():
    """Função principal que executa todas as verificações"""
    checks = {
        "timestamp": datetime.now().isoformat(),
        "installed_packages": check_installed_packages(),
        "requirements": check_requirements(),
        "virtual_env": check_venv(),
    }

    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
