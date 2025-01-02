"""Utilidades para testes."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def create_test_embate(
    titulo: str,
    tipo: str = "tecnico",
    contexto: str = "Contexto de teste",
    status: str = "aberto",
    argumentos: list[dict[str, Any]] | None = None,
    decisao: str | None = None,
    razao: str | None = None
) -> dict[str, Any]:
    """
    Cria um dicionário com dados de embate para teste.
    
    Args:
        titulo: Título do embate
        tipo: Tipo do embate (tecnico/preferencia)
        contexto: Contexto do embate
        status: Status do embate (aberto/resolvido)
        argumentos: Lista de argumentos
        decisao: Decisão do embate
        razao: Razão da decisão
    
    Returns:
        Dicionário com os dados do embate
    """
    if argumentos is None:
        argumentos = []
    
    return {
        "titulo": titulo,
        "tipo": tipo,
        "contexto": contexto,
        "status": status,
        "data_inicio": datetime.now().isoformat(),
        "argumentos": argumentos,
        "decisao": decisao,
        "razao": razao,
        "arquivo": f"embate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    }

def create_test_argumento(
    autor: str,
    conteudo: str,
    tipo: str = "tecnico"
) -> dict[str, Any]:
    """
    Cria um dicionário com dados de argumento para teste.
    
    Args:
        autor: Autor do argumento
        conteudo: Conteúdo do argumento
        tipo: Tipo do argumento (tecnico/preferencia)
    
    Returns:
        Dicionário com os dados do argumento
    """
    return {
        "autor": autor,
        "conteudo": conteudo,
        "tipo": tipo,
        "data": datetime.now().isoformat()
    }

def create_test_embate_file(
    dir_path: Path,
    embate_data: dict[str, Any]
) -> Path:
    """
    Cria um arquivo de embate para teste.
    
    Args:
        dir_path: Diretório onde criar o arquivo
        embate_data: Dados do embate
    
    Returns:
        Path do arquivo criado
    """
    file_path = dir_path / embate_data["arquivo"]
    with open(file_path, "w") as f:
        json.dump(embate_data, f, indent=2)
    return file_path

def create_test_rules_file(
    dir_path: Path,
    tema: str,
    embates: list[dict[str, Any]]
) -> Path:
    """
    Cria um arquivo de regras para teste.
    
    Args:
        dir_path: Diretório onde criar o arquivo
        tema: Tema das regras
        embates: Lista de embates incluídos
    
    Returns:
        Path do arquivo criado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = dir_path / f"regras_{timestamp}.md"
    
    content = [
        f"# Regras: {tema}",
        "",
        "## Contexto",
        "",
        "Este documento condensa as decisões e regras estabelecidas a partir dos seguintes contextos:",
        ""
    ]
    
    # Adiciona contextos
    for embate in embates:
        content.append(f"- {embate['contexto']}")
    
    content.extend([
        "",
        "## Decisões",
        ""
    ])
    
    # Adiciona decisões
    for embate in embates:
        if embate["decisao"]:
            content.extend([
                f"### {embate['titulo']}",
                "",
                f"**Decisão:** {embate['decisao']}",
                "",
                f"**Razão:** {embate['razao']}",
                "",
                "**Argumentos considerados:**",
                ""
            ])
            for arg in embate["argumentos"]:
                content.append(f"- {arg['conteudo']} (por {arg['autor']}, {arg['tipo']})")
            content.append("")
    
    # Adiciona metadados
    content.extend([
        "## Metadados",
        "",
        f"- Data de condensação: {datetime.now().isoformat()}",
        f"- Embates processados: {len(embates)}",
        "- Arquivos removidos após condensação:"
    ])
    
    for embate in embates:
        content.append(f"  - {embate['arquivo']}")
    
    with open(file_path, "w") as f:
        f.write("\n".join(content))
    
    return file_path

def verify_embate_format(embate_data: dict[str, Any]) -> bool:
    """
    Verifica se os dados do embate estão no formato correto.
    
    Args:
        embate_data: Dados do embate para verificar
    
    Returns:
        True se o formato estiver correto, False caso contrário
    """
    required_fields = {
        "titulo": str,
        "tipo": str,
        "contexto": str,
        "status": str,
        "data_inicio": str,
        "argumentos": list,
        "arquivo": str
    }
    
    # Verifica campos obrigatórios
    for field, field_type in required_fields.items():
        if field not in embate_data:
            return False
        if not isinstance(embate_data[field], field_type):
            return False
    
    # Verifica valores permitidos
    if embate_data["tipo"] not in ["tecnico", "preferencia"]:
        return False
    if embate_data["status"] not in ["aberto", "resolvido"]:
        return False
    
    # Verifica formato da data
    try:
        datetime.fromisoformat(embate_data["data_inicio"])
    except ValueError:
        return False
    
    # Verifica argumentos
    for arg in embate_data["argumentos"]:
        if not verify_argumento_format(arg):
            return False
    
    # Verifica consistência de status e decisão
    if embate_data["status"] == "resolvido":
        if "decisao" not in embate_data or "razao" not in embate_data:
            return False
        if not embate_data["decisao"] or not embate_data["razao"]:
            return False
    
    return True

def verify_argumento_format(arg_data: dict[str, Any]) -> bool:
    """
    Verifica se os dados do argumento estão no formato correto.
    
    Args:
        arg_data: Dados do argumento para verificar
    
    Returns:
        True se o formato estiver correto, False caso contrário
    """
    required_fields = {
        "autor": str,
        "conteudo": str,
        "tipo": str,
        "data": str
    }
    
    # Verifica campos obrigatórios
    for field, field_type in required_fields.items():
        if field not in arg_data:
            return False
        if not isinstance(arg_data[field], field_type):
            return False
    
    # Verifica valores permitidos
    if arg_data["tipo"] not in ["tecnico", "preferencia"]:
        return False
    
    # Verifica formato da data
    try:
        datetime.fromisoformat(arg_data["data"])
    except ValueError:
        return False
    
    return True

def verify_rules_format(file_path: Path) -> bool:
    """
    Verifica se o arquivo de regras está no formato correto.
    
    Args:
        file_path: Caminho do arquivo de regras
    
    Returns:
        True se o formato estiver correto, False caso contrário
    """
    if not file_path.exists() or not file_path.is_file():
        return False
    
    content = file_path.read_text()
    
    # Verifica seções obrigatórias
    required_sections = [
        "# Regras:",
        "## Contexto",
        "## Decisões",
        "## Metadados"
    ]
    
    for section in required_sections:
        if section not in content:
            return False
    
    # Verifica formato do nome do arquivo
    if not re.match(r"regras_\d{8}_\d{6}\.md", file_path.name):
        return False
    
    # Verifica metadados
    if not re.search(r"- Data de condensação: \d{4}-\d{2}-\d{2}", content):
        return False
    if not re.search(r"- Embates processados: \d+", content):
        return False
    if "- Arquivos removidos após condensação:" not in content:
        return False
    
    return True 