"""Testes de integração para sincronização com Supabase."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend_rag_ia.cli.c_embates_saudaveis import CondensadorEmbates
from backend_rag_ia.services.semantic_search import SemanticSearchManager


# Fixtures
@pytest.fixture
def mock_supabase():
    """Mock do cliente Supabase."""
    mock = MagicMock()
    mock.rpc.return_value.execute.return_value = {"data": {"id": 1}}
    return mock

@pytest.fixture
def mock_semantic_manager():
    """Mock do SemanticSearchManager."""
    manager = MagicMock(spec=SemanticSearchManager)
    manager._get_embedding.return_value = [0.1, 0.2, 0.3]
    return manager

@pytest.fixture
def temp_dirs(tmp_path):
    """Cria diretórios temporários para embates e regras."""
    embates_dir = tmp_path / "embates"
    regras_dir = tmp_path / "regras"
    embates_dir.mkdir()
    regras_dir.mkdir()
    return embates_dir, regras_dir

@pytest.fixture
def sample_embate_file(temp_dirs):
    """Cria um arquivo de embate de exemplo."""
    embates_dir = temp_dirs[0]
    embate_file = embates_dir / "embate_test.json"
    
    embate_data = {
        "titulo": "Teste Supabase",
        "tipo": "tecnico",
        "contexto": "Teste de sincronização",
        "status": "resolvido",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [
            {
                "autor": "AI",
                "tipo": "tecnico",
                "conteudo": "Argumento teste",
                "data": datetime.now().isoformat()
            }
        ],
        "decisao": "Decisão teste",
        "razao": "Razão teste",
        "arquivo": "embate_test.json"
    }
    
    with open(embate_file, "w") as f:
        json.dump(embate_data, f)
    
    return embate_file

# Testes
@pytest.mark.asyncio
async def test_supabase_sync_success(temp_dirs, mock_supabase, mock_semantic_manager, sample_embate_file):
    """Testa sincronização bem-sucedida com Supabase."""
    embates_dir, regras_dir = temp_dirs
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase", mock_supabase), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager):
        
        condensador = CondensadorEmbates(
            dir_embates=str(embates_dir),
            dir_regras=str(regras_dir),
            min_embates_tema=1,
            auto_sync=True
        )
        
        # Processa e sincroniza
        arquivos_gerados = await condensador.processar()
        
        # Verifica se as regras foram geradas
        assert len(arquivos_gerados) == 1
        
        # Verifica se a função RPC foi chamada
        mock_supabase.rpc.assert_called_with(
            "inserir_regra_condensada_com_embedding",
            {
                "p_arquivo": arquivos_gerados[0].name,
                "p_conteudo": pytest.approx({"text": arquivos_gerados[0].read_text()}),
                "p_metadata": pytest.approx({"tema": "Teste Supabase", "num_embates": 1}),
                "p_embedding": [0.1, 0.2, 0.3]
            }
        )

@pytest.mark.asyncio
async def test_supabase_sync_error(temp_dirs, mock_supabase, mock_semantic_manager, sample_embate_file):
    """Testa tratamento de erro na sincronização com Supabase."""
    embates_dir, regras_dir = temp_dirs
    
    # Configura mock para simular erro
    mock_supabase.rpc.side_effect = Exception("Supabase error")
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase", mock_supabase), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager):
        
        condensador = CondensadorEmbates(
            dir_embates=str(embates_dir),
            dir_regras=str(regras_dir),
            min_embates_tema=1,
            auto_sync=True
        )
        
        # Processa e tenta sincronizar
        with pytest.raises(Exception) as exc_info:
            await condensador.processar()
        
        assert "Supabase error" in str(exc_info.value)
        
        # Verifica se os arquivos originais ainda existem
        assert sample_embate_file.exists()

@pytest.mark.asyncio
async def test_supabase_sync_disabled(temp_dirs, mock_supabase, mock_semantic_manager, sample_embate_file):
    """Testa processamento com sincronização desabilitada."""
    embates_dir, regras_dir = temp_dirs
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase", mock_supabase), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager):
        
        condensador = CondensadorEmbates(
            dir_embates=str(embates_dir),
            dir_regras=str(regras_dir),
            min_embates_tema=1,
            auto_sync=False  # Desabilita sincronização
        )
        
        # Processa sem sincronizar
        arquivos_gerados = await condensador.processar()
        
        # Verifica se as regras foram geradas
        assert len(arquivos_gerados) == 1
        
        # Verifica que Supabase não foi chamado
        mock_supabase.rpc.assert_not_called()

@pytest.mark.asyncio
async def test_supabase_sync_retry(temp_dirs, mock_supabase, mock_semantic_manager, sample_embate_file):
    """Testa retry na sincronização com Supabase."""
    embates_dir, regras_dir = temp_dirs
    
    # Configura mock para falhar na primeira tentativa
    mock_supabase.rpc.side_effect = [
        Exception("Temporary error"),
        {"data": {"id": 1}}
    ]
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase", mock_supabase), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager):
        
        condensador = CondensadorEmbates(
            dir_embates=str(embates_dir),
            dir_regras=str(regras_dir),
            min_embates_tema=1,
            auto_sync=True
        )
        
        # Processa com retry
        arquivos_gerados = await condensador.processar()
        
        # Verifica se as regras foram geradas
        assert len(arquivos_gerados) == 1
        
        # Verifica que houve duas tentativas
        assert mock_supabase.rpc.call_count == 2

@pytest.mark.asyncio
async def test_supabase_sync_multiple_embates(temp_dirs, mock_supabase, mock_semantic_manager):
    """Testa sincronização de múltiplos embates."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria múltiplos embates
    for i in range(3):
        embate_file = embates_dir / f"embate_{i}.json"
        embate_data = {
            "titulo": f"Teste {i}",
            "tipo": "tecnico",
            "contexto": "Contexto comum",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [],
            "decisao": f"Decisão {i}",
            "razao": f"Razão {i}",
            "arquivo": f"embate_{i}.json"
        }
        with open(embate_file, "w") as f:
            json.dump(embate_data, f)
    
    with patch("backend_rag_ia.cli.c_embates_saudaveis.supabase", mock_supabase), \
         patch("backend_rag_ia.cli.c_embates_saudaveis.semantic_manager", mock_semantic_manager):
        
        condensador = CondensadorEmbates(
            dir_embates=str(embates_dir),
            dir_regras=str(regras_dir),
            min_embates_tema=2,
            auto_sync=True
        )
        
        # Processa e sincroniza
        arquivos_gerados = await condensador.processar()
        
        # Verifica se as regras foram geradas e sincronizadas
        assert len(arquivos_gerados) > 0
        assert mock_supabase.rpc.call_count == len(arquivos_gerados) 