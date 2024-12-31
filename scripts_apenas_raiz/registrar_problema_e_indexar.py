#!/usr/bin/env python3
"""Script para registrar problemas conhecidos no projeto."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


def adicionar_problema(
    categoria: str,
    titulo: str,
    problema: str,
    erro: str,
    solucao: str,
    prevencao: str,
) -> None:
    """Adiciona um novo problema ao arquivo PROBLEMAS_CONHECIDOS.md.

    Args:
        categoria: Categoria do problema (ex: "NumPy", "Estrutura")
        titulo: Título breve do problema
        problema: Descrição detalhada do problema
        erro: Mensagem de erro ou descrição do erro
        solucao: Como o problema foi resolvido
        prevencao: Como evitar o problema no futuro

    Raises:
        FileNotFoundError: Se o arquivo de problemas conhecidos não existir
        PermissionError: Se não houver permissão para escrever no arquivo
    """
    data = date.today().isoformat()
    entrada = f"""
### {data} - {categoria} - {titulo}

**Problema:** {problema}
**Erro:** {erro}
**Solução:** {solucao}
**Prevenção:** {prevencao}
"""

    arquivo_path = Path("backend_rag_ia/regras_md/PROBLEMAS_CONHECIDOS.md")
    try:
        arquivo_path.parent.mkdir(parents=True, exist_ok=True)
        arquivo_path.write_text(entrada, encoding="utf-8", mode="a")
        print(f"✅ Problema registrado em {arquivo_path}")
    except (FileNotFoundError, PermissionError) as e:
        print(f"❌ Erro ao registrar problema: {e}")
        raise


def carregar_dados_problema(nome_arquivo: str) -> dict[str, Any]:
    """Carrega os dados do problema do arquivo JSON.

    Args:
        nome_arquivo: Nome do arquivo JSON (sem extensão)

    Returns:
        Dicionário com os dados do problema

    Raises:
        FileNotFoundError: Se o arquivo JSON não existir
        json.JSONDecodeError: Se o arquivo JSON estiver mal formatado
    """
    json_path = Path("backend_rag_ia/dados/problemas_conhecidos") / f"{nome_arquivo}.json"

    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {json_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        raise


def main() -> None:
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Registra um problema conhecido")
    parser.add_argument(
        "--nome",
        required=True,
        help="Nome do arquivo JSON (sem extensão) em backend_rag_ia/dados/problemas_conhecidos/",
    )

    try:
        args = parser.parse_args()
        dados = carregar_dados_problema(args.nome)
        adicionar_problema(
            dados["categoria"],
            dados["titulo"],
            dados["problema"],
            dados["erro"],
            dados["solucao"],
            dados["prevencao"],
        )
        print("\n⚠️ Nota: A reindexação da documentação será implementada em breve!")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Erro: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
