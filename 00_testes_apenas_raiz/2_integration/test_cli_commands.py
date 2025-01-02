"""Testes de integração para comandos CLI."""

import pytest
from pathlib import Path
from datetime import datetime
import json
from click.testing import CliRunner
from rich.progress import Progress
from backend_rag_ia.cli.c_embates_saudaveis import (
    edit_embate,
    search_content,
    export_embates,
    import_embates,
    manage_tags
)

@pytest.fixture
def cli_runner():
    """Fixture que fornece um runner para testes CLI."""
    return CliRunner()

@pytest.fixture
def sample_embate(temp_test_dir):
    """Cria um embate de exemplo para testes."""
    embate_data = {
        "titulo": "Teste CLI",
        "tipo": "tecnico",
        "contexto": "Teste de comandos CLI",
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [
            {
                "autor": "AI",
                "tipo": "tecnico",
                "conteudo": "Argumento de teste",
                "data": datetime.now().isoformat()
            }
        ],
        "decisao": None,
        "razao": None,
        "arquivo": "embate_cli_test.json",
        "tags": ["teste", "cli"]
    }
    
    file_path = temp_test_dir["embates"] / embate_data["arquivo"]
    with open(file_path, "w") as f:
        json.dump(embate_data, f)
    
    return file_path

def test_edit_embate(cli_runner, sample_embate):
    """Testa o comando de edição de embates."""
    # Testa edição de título
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--campo", "titulo",
        "--valor", "Novo Título"
    ])
    assert result.exit_code == 0
    assert "Embate atualizado com sucesso" in result.output
    
    # Verifica se a alteração foi salva
    with open(sample_embate) as f:
        data = json.load(f)
        assert data["titulo"] == "Novo Título"
    
    # Testa edição inválida
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--campo", "campo_invalido",
        "--valor", "teste"
    ])
    assert result.exit_code != 0
    assert "Campo inválido" in result.output

def test_search_content(cli_runner, temp_test_dir, sample_embate):
    """Testa o comando de busca de conteúdo."""
    # Busca por texto
    result = cli_runner.invoke(search_content, [
        "--texto", "Argumento de teste",
        "--dir", str(temp_test_dir["embates"])
    ])
    assert result.exit_code == 0
    assert "embate_cli_test.json" in result.output
    assert "Argumento de teste" in result.output
    
    # Busca por tag
    result = cli_runner.invoke(search_content, [
        "--tag", "cli",
        "--dir", str(temp_test_dir["embates"])
    ])
    assert result.exit_code == 0
    assert "embate_cli_test.json" in result.output
    
    # Busca sem resultados
    result = cli_runner.invoke(search_content, [
        "--texto", "conteúdo inexistente",
        "--dir", str(temp_test_dir["embates"])
    ])
    assert result.exit_code == 0
    assert "Nenhum resultado encontrado" in result.output

def test_export_import_embates(cli_runner, temp_test_dir, sample_embate):
    """Testa os comandos de exportação e importação de embates."""
    export_dir = temp_test_dir["root"] / "export"
    export_dir.mkdir()
    
    # Exporta embates
    result = cli_runner.invoke(export_embates, [
        "--dir-origem", str(temp_test_dir["embates"]),
        "--dir-destino", str(export_dir),
        "--tags", "cli,teste"
    ])
    assert result.exit_code == 0
    assert "Embates exportados com sucesso" in result.output
    
    # Verifica arquivo exportado
    export_file = export_dir / "embates_export.zip"
    assert export_file.exists()
    
    # Limpa diretório de embates
    sample_embate.unlink()
    
    # Importa embates
    result = cli_runner.invoke(import_embates, [
        "--arquivo", str(export_file),
        "--dir-destino", str(temp_test_dir["embates"])
    ])
    assert result.exit_code == 0
    assert "Embates importados com sucesso" in result.output
    
    # Verifica se o embate foi restaurado
    assert (temp_test_dir["embates"] / "embate_cli_test.json").exists()

def test_manage_tags(cli_runner, sample_embate):
    """Testa o comando de gerenciamento de tags."""
    # Adiciona tag
    result = cli_runner.invoke(manage_tags, [
        str(sample_embate),
        "--adicionar", "nova_tag"
    ])
    assert result.exit_code == 0
    assert "Tag adicionada com sucesso" in result.output
    
    # Verifica se a tag foi adicionada
    with open(sample_embate) as f:
        data = json.load(f)
        assert "nova_tag" in data["tags"]
    
    # Remove tag
    result = cli_runner.invoke(manage_tags, [
        str(sample_embate),
        "--remover", "teste"
    ])
    assert result.exit_code == 0
    assert "Tag removida com sucesso" in result.output
    
    # Verifica se a tag foi removida
    with open(sample_embate) as f:
        data = json.load(f)
        assert "teste" not in data["tags"]
    
    # Lista tags
    result = cli_runner.invoke(manage_tags, [
        str(sample_embate),
        "--listar"
    ])
    assert result.exit_code == 0
    assert "cli" in result.output
    assert "nova_tag" in result.output

def test_progress_bars():
    """Testa a exibição de progress bars em operações longas."""
    with Progress() as progress:
        # Simula uma operação longa
        task = progress.add_task("Processando...", total=100)
        
        for i in range(100):
            # Simula algum trabalho
            progress.update(task, advance=1)
        
        # Verifica se a barra completou
        assert progress.tasks[0].completed
        assert progress.tasks[0].percentage == 100

def test_interactive_validation(cli_runner, sample_embate):
    """Testa a validação interativa de inputs."""
    # Testa validação de tipo
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--campo", "tipo",
        "--valor", "tipo_invalido"
    ])
    assert result.exit_code != 0
    assert "Tipo inválido. Use 'tecnico' ou 'preferencia'" in result.output
    
    # Testa validação de status
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--campo", "status",
        "--valor", "status_invalido"
    ])
    assert result.exit_code != 0
    assert "Status inválido. Use 'aberto' ou 'resolvido'" in result.output

def test_operation_confirmation(cli_runner, sample_embate):
    """Testa confirmações para operações críticas."""
    # Tenta excluir sem confirmar
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--excluir"
    ], input="n\n")  # Responde "não" para confirmação
    assert result.exit_code == 0
    assert sample_embate.exists()
    
    # Exclui com confirmação
    result = cli_runner.invoke(edit_embate, [
        str(sample_embate),
        "--excluir"
    ], input="s\n")  # Responde "sim" para confirmação
    assert result.exit_code == 0
    assert not sample_embate.exists() 