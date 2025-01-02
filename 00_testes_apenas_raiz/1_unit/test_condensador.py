"""Testes unitários para a classe CondensadorEmbates."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from backend_rag_ia.utils.logging_config import logger

from backend_rag_ia.services.semantic_search import SemanticSearchManager
from backend_rag_ia.config.settings import get_settings

# Fixtures específicas para testes do condensador
@pytest.fixture
def mock_semantic_manager():
    """Mock do SemanticSearchManager."""
    manager = Mock(spec=SemanticSearchManager)
    manager._get_embedding.return_value = [0.1, 0.2, 0.3]
    return manager

@pytest.fixture
def mock_settings():
    """Mock das configurações."""
    settings = Mock()
    settings.LOCAL_URL = "http://localhost:10000"
    return settings

@pytest.fixture
def condensador(tmp_path, mock_semantic_manager, mock_settings):
    """Fixture que cria um CondensadorEmbates com diretórios temporários."""
    from backend_rag_ia.cli.c_embates_saudaveis import CondensadorEmbates
    
    dir_embates = tmp_path / "embates"
    dir_regras = tmp_path / "regras"
    dir_embates.mkdir()
    dir_regras.mkdir()
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.settings", mock_settings):
        return CondensadorEmbates(
            dir_embates=str(dir_embates),
            dir_regras=str(dir_regras)
        )

# Testes dos métodos individuais
def test_verificar_status_sistema(condensador, mock_settings):
    """Testa o método de verificação de status do sistema."""
    with patch("requests.get") as mock_get:
        # Teste com sistema saudável
        mock_get.return_value.status_code = 200
        assert condensador.verificar_status_sistema() is True
        
        # Teste com sistema indisponível
        mock_get.return_value.status_code = 500
        assert condensador.verificar_status_sistema() is False
        
        # Teste com erro de conexão
        mock_get.side_effect = Exception("Connection error")
        assert condensador.verificar_status_sistema() is False

def test_carregar_embates(condensador, tmp_path):
    """Testa o carregamento de embates do diretório."""
    # Cria um arquivo de embate de teste
    embate_file = tmp_path / "embates" / "embate_test.json"
    embate_data = {
        "titulo": "Teste",
        "tipo": "tecnico",
        "contexto": "Contexto de teste",
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [],
        "decisao": None,
        "razao": None,
        "arquivo": "embate_test.json"
    }
    
    with open(embate_file, "w") as f:
        import json
        json.dump(embate_data, f)
    
    # Testa carregamento
    embates = condensador.carregar_embates()
    assert len(embates) == 1
    assert embates[0].titulo == "Teste"
    
    # Testa erro ao carregar arquivo inválido
    with open(tmp_path / "embates" / "embate_invalid.json", "w") as f:
        f.write("invalid json")
    
    embates = condensador.carregar_embates()
    assert len(embates) == 1  # Apenas o arquivo válido é carregado

@pytest.mark.asyncio
async def test_sincronizar_com_supabase(condensador, tmp_path):
    """Testa a sincronização com Supabase."""
    arquivo = tmp_path / "test_rules.md"
    arquivo.write_text("# Test Rules")
    
    embates = []  # Lista mock de embates
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase") as mock_supabase:
        mock_rpc = MagicMock()
        mock_supabase.rpc.return_value = mock_rpc
        
        await condensador.sincronizar_com_supabase(arquivo, "test", embates)
        
        # Verifica se a função RPC foi chamada com os parâmetros corretos
        mock_supabase.rpc.assert_called_once_with(
            "inserir_regra_condensada_com_embedding",
            {
                "p_arquivo": arquivo.name,
                "p_conteudo": '{"text": "# Test Rules"}',
                "p_metadata": pytest.approx({"tema": "test", "num_embates": 0}),
                "p_embedding": [0.1, 0.2, 0.3]
            }
        )

def test_gerar_regras_md(condensador):
    """Testa a geração de conteúdo markdown."""
    from backend_rag_ia.cli.c_embates_saudaveis import Embate, Argumento
    
    embates = [
        Embate(
            titulo="Teste",
            tipo="tecnico",
            contexto="Contexto de teste",
            status="resolvido",
            data_inicio=datetime.now(),
            argumentos=[
                Argumento(
                    autor="AI",
                    tipo="tecnico",
                    conteudo="Argumento teste",
                    data=datetime.now()
                )
            ],
            decisao="Decisão teste",
            razao="Razão teste",
            arquivo="embate_test.json"
        )
    ]
    
    md = condensador.gerar_regras_md("Tema Teste", embates)
    
    assert "# Regras: Tema Teste" in md
    assert "Contexto de teste" in md
    assert "Decisão teste" in md
    assert "Razão teste" in md
    assert "Argumento teste" in md

def test_salvar_regras(condensador, tmp_path):
    """Testa o salvamento de regras em arquivo."""
    tema = "test"
    conteudo = "# Test Rules"
    
    arquivo = condensador.salvar_regras(tema, conteudo)
    
    assert arquivo.exists()
    assert arquivo.read_text() == conteudo
    assert str(arquivo).endswith(".md")
    assert tema.lower() in str(arquivo)

def test_arquivar_embates(condensador, tmp_path):
    """Testa o arquivamento de embates."""
    from backend_rag_ia.cli.c_embates_saudaveis import Embate
    
    # Cria um embate de teste
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="Contexto",
        status="resolvido",
        data_inicio=datetime.now(),
        argumentos=[],
        decisao="Decisão",
        razao="Razão",
        arquivo="embate_test.json"
    )
    
    # Cria o arquivo do embate
    embate_file = tmp_path / "embates" / embate.arquivo
    embate_file.write_text("test content")
    
    # Testa arquivamento
    condensador.arquivar_embates([embate])
    
    # Verifica se o arquivo foi movido e depois removido
    assert not embate_file.exists()
    assert not (tmp_path / "embates" / "arquivo" / embate.arquivo).exists() 