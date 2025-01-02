"""Testes de integração para o fluxo completo de embates."""

import json
from pathlib import Path

import pytest

from backend_rag_ia.cli.c_embates_saudaveis import (
    CondensadorEmbates,
    adicionar_argumento,
    iniciar,
    resolver,
)


@pytest.fixture
def temp_embates_dir(tmp_path):
    """Fixture que cria um diretório temporário para os embates."""
    embates_dir = tmp_path / "embates"
    embates_dir.mkdir()
    return embates_dir

@pytest.fixture
def temp_regras_dir(tmp_path):
    """Fixture que cria um diretório temporário para as regras."""
    regras_dir = tmp_path / "regras"
    regras_dir.mkdir()
    return regras_dir

@pytest.mark.asyncio
async def test_complete_embate_flow(temp_embates_dir, temp_regras_dir):
    """Testa o fluxo completo de um embate, do início à resolução."""
    # 1. Iniciar embate
    titulo = "Teste de Integração"
    tipo = "tecnico"
    contexto = "Testando fluxo completo"
    
    iniciar(titulo, tipo, contexto)
    
    # Verifica se o arquivo foi criado
    embate_files = list(temp_embates_dir.glob("embate_*.json"))
    assert len(embate_files) == 1
    
    # 2. Adicionar argumentos
    adicionar_argumento(
        titulo=titulo,
        autor="AI",
        tipo="tecnico",
        conteudo="Primeiro argumento"
    )
    
    adicionar_argumento(
        titulo=titulo,
        autor="Humano",
        tipo="tecnico",
        conteudo="Segundo argumento"
    )
    
    # Verifica se os argumentos foram adicionados
    with open(embate_files[0]) as f:
        dados = json.load(f)
        assert len(dados["argumentos"]) == 2
        assert dados["argumentos"][0]["conteudo"] == "Primeiro argumento"
        assert dados["argumentos"][1]["conteudo"] == "Segundo argumento"
    
    # 3. Resolver embate
    decisao = "Decisão final"
    razao = "Razão da decisão"
    
    resolver(titulo, decisao, razao)
    
    # Verifica se o embate foi resolvido
    with open(embate_files[0]) as f:
        dados = json.load(f)
        assert dados["status"] == "resolvido"
        assert dados["decisao"] == decisao
        assert dados["razao"] == razao
    
    # 4. Verificar registro no arquivo de decisões
    registro_path = Path("01_regras_md_apenas_raiz/1_core/j_registro_decisoes.md")
    if registro_path.exists():
        conteudo = registro_path.read_text()
        assert titulo in conteudo
        assert decisao in conteudo
        assert razao in conteudo
    
    # 5. Processar com CondensadorEmbates
    condensador = CondensadorEmbates(
        dir_embates=str(temp_embates_dir),
        dir_regras=str(temp_regras_dir),
        min_embates_tema=1  # Reduzido para teste
    )
    
    arquivos_gerados = await condensador.processar()
    
    # Verifica se as regras foram geradas
    assert len(arquivos_gerados) == 1
    regras_md = arquivos_gerados[0].read_text()
    assert titulo in regras_md
    assert decisao in regras_md
    assert razao in regras_md
    
    # 6. Verificar se o embate foi arquivado
    assert not embate_files[0].exists()

@pytest.mark.asyncio
async def test_multiple_embates_flow(temp_embates_dir, temp_regras_dir):
    """Testa o fluxo com múltiplos embates relacionados."""
    # 1. Criar embates relacionados
    embates = [
        {
            "titulo": f"Embate {i}",
            "tipo": "tecnico",
            "contexto": "Contexto comum",
            "argumentos": [f"Argumento {j}" for j in range(2)]
        }
        for i in range(3)
    ]
    
    # 2. Processar cada embate
    for embate in embates:
        # Iniciar
        iniciar(embate["titulo"], embate["tipo"], embate["contexto"])
        
        # Adicionar argumentos
        for j, arg in enumerate(embate["argumentos"]):
            adicionar_argumento(
                titulo=embate["titulo"],
                autor=f"Autor {j}",
                tipo="tecnico",
                conteudo=arg
            )
        
        # Resolver
        resolver(
            titulo=embate["titulo"],
            decisao=f"Decisão do {embate['titulo']}",
            razao=f"Razão do {embate['titulo']}"
        )
    
    # 3. Processar com CondensadorEmbates
    condensador = CondensadorEmbates(
        dir_embates=str(temp_embates_dir),
        dir_regras=str(temp_regras_dir),
        min_embates_tema=2
    )
    
    arquivos_gerados = await condensador.processar()
    
    # Verifica se as regras foram condensadas
    assert len(arquivos_gerados) > 0
    
    # Verifica o conteúdo das regras
    for arquivo in arquivos_gerados:
        conteudo = arquivo.read_text()
        assert "Contexto comum" in conteudo
        assert "Embate" in conteudo
        assert "Decisão" in conteudo
        assert "Razão" in conteudo

@pytest.mark.asyncio
async def test_error_handling_flow(temp_embates_dir, temp_regras_dir):
    """Testa o tratamento de erros no fluxo de embates."""
    # 1. Tentar resolver embate inexistente
    with pytest.raises(FileNotFoundError, match="Embate não encontrado"):
        resolver(
            titulo="Inexistente",
            decisao="Não deve funcionar",
            razao="Embate não existe"
        )
    
    # 2. Tentar adicionar argumento a embate inexistente
    with pytest.raises(FileNotFoundError, match="Embate não encontrado"):
        adicionar_argumento(
            titulo="Inexistente",
            autor="AI",
            tipo="tecnico",
            conteudo="Não deve funcionar"
        )
    
    # 3. Criar embate e tentar operações inválidas
    titulo = "Teste Erros"
    iniciar(titulo, "tecnico", "Contexto")
    
    # Tentar resolver sem argumentos
    resolver(titulo, "Decisão", "Razão")  # Deve funcionar, mas gerar aviso
    
    # Tentar adicionar argumento após resolução
    with pytest.raises(ValueError, match="Embate já está resolvido"):
        adicionar_argumento(
            titulo=titulo,
            autor="AI",
            tipo="tecnico",
            conteudo="Não deve funcionar"
        )
    
    # 4. Testar CondensadorEmbates com diretório vazio
    condensador = CondensadorEmbates(
        dir_embates=str(temp_embates_dir),
        dir_regras=str(temp_regras_dir)
    )
    
    arquivos_gerados = await condensador.processar()
    assert len(arquivos_gerados) == 0  # Não deve gerar arquivos 