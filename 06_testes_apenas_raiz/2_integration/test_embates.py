"""Testes de integração para o sistema de embates."""
import pytest
from pathlib import Path
import json
from datetime import datetime
from backend_rag_ia.config.settings import get_settings
from cli.c_embates_saudaveis import CondensadorEmbates, Embate, Argumento

settings = get_settings()

@pytest.fixture
def dir_teste(tmp_path):
    """Cria diretórios temporários para teste."""
    embates_dir = tmp_path / "embates"
    regras_dir = tmp_path / "regras"
    embates_dir.mkdir()
    regras_dir.mkdir()
    return {"embates": embates_dir, "regras": regras_dir}

@pytest.fixture
def embates_exemplo(dir_teste):
    """Cria embates de exemplo para teste."""
    embates = [
        {
            "titulo": "Teste API 1",
            "tipo": "tecnico",
            "contexto": "Contexto do teste 1",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "Dev1",
                    "conteudo": "Argumento 1",
                    "tipo": "tecnico",
                    "data": datetime.now().isoformat()
                }
            ],
            "decisao": "Decisão 1",
            "razao": "Razão 1"
        },
        {
            "titulo": "Teste API 2",
            "tipo": "tecnico",
            "contexto": "Contexto do teste 2",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "Dev2",
                    "conteudo": "Argumento 2",
                    "tipo": "tecnico",
                    "data": datetime.now().isoformat()
                }
            ],
            "decisao": "Decisão 2",
            "razao": "Razão 2"
        }
    ]
    
    # Salva embates em arquivos
    for i, embate in enumerate(embates):
        arquivo = dir_teste["embates"] / f"embate_teste_{i}.json"
        with open(arquivo, "w") as f:
            json.dump(embate, f)
    
    return embates

@pytest.mark.asyncio
async def test_carregar_embates(dir_teste, embates_exemplo):
    """Testa carregamento de embates."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"]),
        min_embates_tema=1
    )
    
    embates = condensador.carregar_embates()
    assert len(embates) == 2
    assert all(isinstance(e, Embate) for e in embates)
    assert embates[0].titulo == "Teste API 1"
    assert embates[1].titulo == "Teste API 2"

@pytest.mark.asyncio
async def test_agrupar_por_tema(dir_teste, embates_exemplo):
    """Testa agrupamento de embates por tema."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"]),
        min_embates_tema=1
    )
    
    embates = condensador.carregar_embates()
    grupos = await condensador.agrupar_por_tema(embates)
    
    assert len(grupos) > 0
    for tema, embates_grupo in grupos.items():
        assert all(isinstance(e, Embate) for e in embates_grupo)

@pytest.mark.asyncio
async def test_gerar_regras_md(dir_teste, embates_exemplo):
    """Testa geração de arquivo markdown."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"]),
        min_embates_tema=1
    )
    
    embates = condensador.carregar_embates()
    conteudo = condensador.gerar_regras_md("Teste", embates)
    
    assert "# Regras: Teste" in conteudo
    assert "## Contexto" in conteudo
    assert "## Decisões" in conteudo
    assert "Teste API 1" in conteudo
    assert "Teste API 2" in conteudo

@pytest.mark.asyncio
async def test_processo_completo(dir_teste, embates_exemplo):
    """Testa o processo completo de condensação."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"]),
        min_embates_tema=1,
        auto_sync=False  # Desativa sync com Supabase para teste
    )
    
    arquivos = await condensador.processar()
    
    assert len(arquivos) > 0
    for arquivo in arquivos:
        assert arquivo.exists()
        conteudo = arquivo.read_text()
        assert "# Regras:" in conteudo
        assert "## Contexto" in conteudo
        assert "## Decisões" in conteudo

@pytest.mark.asyncio
async def test_verificar_status_sistema(dir_teste):
    """Testa verificação de status do sistema."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"])
    )
    
    status = condensador.verificar_status_sistema()
    assert isinstance(status, bool)

@pytest.mark.asyncio
async def test_arquivar_embates(dir_teste, embates_exemplo):
    """Testa arquivamento de embates."""
    condensador = CondensadorEmbates(
        dir_embates=str(dir_teste["embates"]),
        dir_regras=str(dir_teste["regras"])
    )
    
    embates = condensador.carregar_embates()
    condensador.arquivar_embates(embates)
    
    # Verifica se os arquivos originais foram movidos
    arquivos_restantes = list(Path(dir_teste["embates"]).glob("embate_*.json"))
    assert len(arquivos_restantes) == 0 