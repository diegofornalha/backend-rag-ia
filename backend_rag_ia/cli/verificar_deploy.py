import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def criar_build_sh():
    """Cria o arquivo build.sh com as configurações necessárias."""
    conteudo = """#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala dependências
pip install -r requirements.txt

# Coleta arquivos estáticos (se necessário)
# python manage.py collectstatic --no-input

# Executa migrações (se necessário)
# python manage.py migrate

# Configurações adicionais
export PORT=10000
export HOST=0.0.0.0
"""

    with open("build.sh", "w") as f:
        f.write(conteudo)

    # Torna o arquivo executável
    os.chmod("build.sh", 0o755)
    console.print("✅ Arquivo build.sh criado e configurado")


def verificar_dockerfile():
    """Verifica se o Dockerfile está configurado corretamente."""
    try:
        with open("Dockerfile", "r") as f:
            conteudo = f.read()

        problemas = []

        # Verifica configurações importantes
        if "EXPOSE 10000" not in conteudo:
            problemas.append("❌ Falta EXPOSE 10000")

        if "WORKDIR /app" not in conteudo:
            problemas.append("❌ Falta WORKDIR /app")

        if "COPY requirements.txt" not in conteudo:
            problemas.append("❌ Falta copiar requirements.txt")

        if problemas:
            console.print("\n🔍 Problemas encontrados no Dockerfile:")
            for problema in problemas:
                console.print(problema)
        else:
            console.print("✅ Dockerfile está configurado corretamente")

    except FileNotFoundError:
        console.print("❌ Dockerfile não encontrado")


def verificar_requirements():
    """Verifica se requirements.txt tem todas as dependências necessárias."""
    try:
        with open("requirements.txt", "r") as f:
            deps = f.read().splitlines()

        deps_necessarias = [
            "gunicorn",
            "python-dotenv",
            "rich",
            "supabase",
            "sentence-transformers",
        ]

        faltando = []
        for dep in deps_necessarias:
            if not any(d.startswith(dep) for d in deps):
                faltando.append(dep)

        if faltando:
            console.print("\n📦 Dependências faltando no requirements.txt:")
            for dep in faltando:
                console.print(f"❌ {dep}")
        else:
            console.print("✅ requirements.txt está completo")

    except FileNotFoundError:
        console.print("❌ requirements.txt não encontrado")


def verificar_render_yaml():
    """Verifica se render.yaml está configurado corretamente."""
    try:
        with open("render.yaml", "r") as f:
            conteudo = f.read()

        checklist = [
            ("services:", "Definição de serviços"),
            ("type: web", "Tipo de serviço"),
            ("name:", "Nome do serviço"),
            ("env:", "Variáveis de ambiente"),
            ("buildCommand:", "Comando de build"),
            ("startCommand:", "Comando de start"),
        ]

        problemas = []
        for termo, descricao in checklist:
            if termo not in conteudo:
                problemas.append(f"❌ Falta {descricao}")

        if problemas:
            console.print("\n🔍 Problemas encontrados no render.yaml:")
            for problema in problemas:
                console.print(problema)
        else:
            console.print("✅ render.yaml está configurado corretamente")

    except FileNotFoundError:
        console.print("❌ render.yaml não encontrado")


def main():
    console.print("\n🚀 Verificador de Deploy Render\n")

    # Verifica e cria build.sh se necessário
    if not os.path.exists("build.sh"):
        console.print("📝 Criando build.sh...")
        criar_build_sh()
    else:
        console.print("✅ build.sh já existe")

    # Verifica outros arquivos
    console.print("\n📋 Verificando configurações...")
    verificar_dockerfile()
    verificar_requirements()
    verificar_render_yaml()

    # Dicas finais
    console.print("\n💡 Próximos passos:")
    console.print("1. Corrija os problemas encontrados")
    console.print("2. Teste localmente usando docker build")
    console.print("3. Faça commit das alterações")
    console.print("4. Push para o repositório")
    console.print("5. Verifique o deploy no dashboard do Render")


if __name__ == "__main__":
    main()
