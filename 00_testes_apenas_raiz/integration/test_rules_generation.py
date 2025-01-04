"""Testes de integração para geração de regras."""

import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from backend_rag_ia.cli.c_embates_saudaveis import CondensadorEmbates


@pytest.fixture
def temp_dirs(tmp_path):
    """Cria diretórios temporários para embates e regras."""
    embates_dir = tmp_path / "embates"
    regras_dir = tmp_path / "regras"
    embates_dir.mkdir()
    regras_dir.mkdir()
    return embates_dir, regras_dir

@pytest.fixture
def sample_embates(temp_dirs):
    """Cria arquivos de embate de exemplo."""
    embates_dir = temp_dirs[0]
    files = []
    
    # Cria embates relacionados
    for i in range(3):
        embate_file = embates_dir / f"embate_{i}.json"
        embate_data = {
            "titulo": f"Teste {i}",
            "tipo": "tecnico",
            "contexto": "Contexto de teste",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": f"Argumento {j} do embate {i}",
                    "data": datetime.now().isoformat()
                }
                for j in range(2)
            ],
            "decisao": f"Decisão do embate {i}",
            "razao": f"Razão do embate {i}",
            "arquivo": f"embate_{i}.json"
        }
        with open(embate_file, "w") as f:
            json.dump(embate_data, f)
        files.append(embate_file)
    
    return files

@pytest.mark.asyncio
async def test_rules_generation_format(temp_dirs, sample_embates):
    """Testa o formato das regras geradas."""
    embates_dir, regras_dir = temp_dirs
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica se as regras foram geradas
    assert len(arquivos_gerados) > 0
    
    for arquivo in arquivos_gerados:
        conteudo = arquivo.read_text()
        
        # Verifica estrutura do markdown
        assert re.search(r"^# Regras:", conteudo, re.MULTILINE)
        assert "## Contexto" in conteudo
        assert "## Decisões" in conteudo
        assert "## Metadados" in conteudo
        
        # Verifica formatação dos argumentos
        assert re.search(r"- \*\*[^*]+\*\* \([^)]+\):", conteudo)
        
        # Verifica presença de decisões
        assert re.search(r"### [^\n]+\n+\*\*Decisão:\*\* ", conteudo)
        
        # Verifica metadados
        assert re.search(r"- Data de condensação: \d{4}-\d{2}-\d{2}", conteudo)
        assert re.search(r"- Embates processados: \d+", conteudo)
        assert re.search(r"- Arquivos removidos após condensação:", conteudo)

@pytest.mark.asyncio
async def test_rules_content_grouping(temp_dirs):
    """Testa o agrupamento de conteúdo nas regras."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria embates com temas relacionados
    temas = ["Frontend", "Frontend", "Backend"]
    for i, tema in enumerate(temas):
        embate_file = embates_dir / f"embate_{i}.json"
        embate_data = {
            "titulo": f"Decisão sobre {tema}",
            "tipo": "tecnico",
            "contexto": f"Contexto sobre {tema}",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": f"Argumento sobre {tema}",
                    "data": datetime.now().isoformat()
                }
            ],
            "decisao": f"Decisão sobre {tema}",
            "razao": f"Razão sobre {tema}",
            "arquivo": f"embate_{i}.json"
        }
        with open(embate_file, "w") as f:
            json.dump(embate_data, f)
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=2
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica se apenas um arquivo foi gerado para Frontend
    assert len(arquivos_gerados) == 1
    
    # Verifica conteúdo do arquivo
    conteudo = arquivos_gerados[0].read_text()
    assert "Frontend" in conteudo
    assert conteudo.count("Decisão sobre Frontend") == 2
    assert "Backend" not in conteudo  # Não deve incluir o embate de Backend

@pytest.mark.asyncio
async def test_rules_file_organization(temp_dirs, sample_embates):
    """Testa a organização dos arquivos de regras."""
    embates_dir, regras_dir = temp_dirs
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    for arquivo in arquivos_gerados:
        # Verifica nome do arquivo
        assert arquivo.name.startswith("regras_")
        assert arquivo.name.endswith(".md")
        assert re.match(r"regras_\d{8}_\d{6}\.md", arquivo.name)
        
        # Verifica estrutura de diretórios
        assert arquivo.parent.is_dir()
        assert str(arquivo.parent).startswith(str(regras_dir))
        
        # Verifica permissões do arquivo
        assert arquivo.exists()
        assert arquivo.is_file()

@pytest.mark.asyncio
async def test_rules_metadata_accuracy(temp_dirs):
    """Testa a precisão dos metadados nas regras geradas."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria embate com dados específicos
    embate_file = embates_dir / "embate_test.json"
    data_inicio = datetime.now()
    embate_data = {
        "titulo": "Teste Metadados",
        "tipo": "tecnico",
        "contexto": "Contexto específico",
        "status": "resolvido",
        "data_inicio": data_inicio.isoformat(),
        "argumentos": [
            {
                "autor": "AI",
                "tipo": "tecnico",
                "conteudo": "Argumento específico",
                "data": data_inicio.isoformat()
            }
        ],
        "decisao": "Decisão específica",
        "razao": "Razão específica",
        "arquivo": "embate_test.json"
    }
    with open(embate_file, "w") as f:
        json.dump(embate_data, f)
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica metadados
    conteudo = arquivos_gerados[0].read_text()
    
    # Verifica data
    data_pattern = r"Data de condensação: (\d{4}-\d{2}-\d{2})"
    match = re.search(data_pattern, conteudo)
    assert match
    data_condensacao = datetime.strptime(match.group(1), "%Y-%m-%d")
    assert data_condensacao.date() == datetime.now().date()
    
    # Verifica contagem de embates
    assert "Embates processados: 1" in conteudo
    
    # Verifica arquivo removido
    assert "embate_test.json" in conteudo 

@pytest.mark.asyncio
async def test_rules_mixed_types(temp_dirs):
    """Testa geração de regras com diferentes tipos de embates."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria embates com diferentes tipos
    tipos = [
        ("tecnico", "Decisão Técnica"),
        ("tecnico", "Arquitetura"),
        ("preferencia", "Estilo de Código"),
        ("preferencia", "Convenções")
    ]
    
    for i, (tipo, tema) in enumerate(tipos):
        embate_file = embates_dir / f"embate_{i}.json"
        embate_data = {
            "titulo": f"{tema} {i}",
            "tipo": tipo,
            "contexto": f"Contexto sobre {tema}",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": tipo,
                    "conteudo": f"Argumento sobre {tema}",
                    "data": datetime.now().isoformat()
                },
                {
                    "autor": "Humano",
                    "tipo": tipo,
                    "conteudo": f"Contra-argumento sobre {tema}",
                    "data": datetime.now().isoformat()
                }
            ],
            "decisao": f"Decisão sobre {tema}",
            "razao": f"Razão sobre {tema}",
            "arquivo": f"embate_{i}.json"
        }
        with open(embate_file, "w") as f:
            json.dump(embate_data, f)
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica se foram gerados arquivos separados para cada tipo
    assert len(arquivos_gerados) == 2  # Um para técnico e outro para preferência
    
    # Verifica conteúdo dos arquivos
    for arquivo in arquivos_gerados:
        conteudo = arquivo.read_text()
        
        if "Decisão Técnica" in conteudo:
            # Verifica arquivo de regras técnicas
            assert "Arquitetura" in conteudo
            assert "Estilo de Código" not in conteudo
            assert "Convenções" not in conteudo
            assert "tipo: tecnico" in conteudo.lower()
        else:
            # Verifica arquivo de regras de preferência
            assert "Estilo de Código" in conteudo
            assert "Convenções" in conteudo
            assert "Decisão Técnica" not in conteudo
            assert "Arquitetura" not in conteudo
            assert "tipo: preferencia" in conteudo.lower()
        
        # Verifica estrutura comum
        assert "## Contexto" in conteudo
        assert "## Decisões" in conteudo
        assert "## Metadados" in conteudo
        assert "**Argumentos considerados:**" in conteudo
        assert "AI" in conteudo
        assert "Humano" in conteudo 

@pytest.mark.asyncio
async def test_rules_with_attachments(temp_dirs):
    """Testa geração de regras com embates que têm anexos."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria diretório de anexos
    anexos_dir = embates_dir / "anexos"
    anexos_dir.mkdir()
    
    # Cria alguns arquivos de anexo
    anexo1 = anexos_dir / "diagrama.png"
    anexo1.write_text("mock image content")
    
    anexo2 = anexos_dir / "exemplo.json"
    anexo2.write_text('{"exemplo": "dados"}')
    
    # Cria embates com anexos
    embates = [
        {
            "titulo": "Decisão com Diagrama",
            "tipo": "tecnico",
            "contexto": "Contexto com diagrama",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": "Veja o diagrama anexo",
                    "data": datetime.now().isoformat(),
                    "anexos": ["diagrama.png"]
                }
            ],
            "decisao": "Decisão baseada no diagrama",
            "razao": "Conforme mostrado no diagrama",
            "arquivo": "embate_diagrama.json",
            "anexos": ["diagrama.png"]
        },
        {
            "titulo": "Decisão com Exemplo",
            "tipo": "tecnico",
            "contexto": "Contexto com exemplo",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": "Veja o exemplo em JSON",
                    "data": datetime.now().isoformat(),
                    "anexos": ["exemplo.json"]
                }
            ],
            "decisao": "Decisão baseada no exemplo",
            "razao": "Conforme mostrado no exemplo",
            "arquivo": "embate_exemplo.json",
            "anexos": ["exemplo.json"]
        }
    ]
    
    # Salva os embates
    for embate in embates:
        with open(embates_dir / embate["arquivo"], "w") as f:
            json.dump(embate, f)
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica se as regras foram geradas
    assert len(arquivos_gerados) == 1
    
    # Verifica conteúdo do arquivo
    conteudo = arquivos_gerados[0].read_text()
    
    # Verifica referências aos anexos
    assert "diagrama.png" in conteudo
    assert "exemplo.json" in conteudo
    
    # Verifica se os anexos foram copiados para o diretório de regras
    regras_anexos_dir = Path(str(regras_dir)) / "anexos"
    assert regras_anexos_dir.exists()
    assert (regras_anexos_dir / "diagrama.png").exists()
    assert (regras_anexos_dir / "exemplo.json").exists()
    
    # Verifica links para os anexos no markdown
    assert re.search(r"\[diagrama\.png\]\(anexos/diagrama\.png\)", conteudo)
    assert re.search(r"\[exemplo\.json\]\(anexos/exemplo\.json\)", conteudo)
    
    # Verifica menções aos anexos nos argumentos
    assert "Veja o diagrama anexo" in conteudo
    assert "Veja o exemplo em JSON" in conteudo
    
    # Verifica menções aos anexos nas decisões
    assert "Decisão baseada no diagrama" in conteudo
    assert "Decisão baseada no exemplo" in conteudo 

@pytest.mark.asyncio
async def test_rules_with_cross_references(temp_dirs):
    """Testa geração de regras com embates que têm referências cruzadas."""
    embates_dir, regras_dir = temp_dirs
    
    # Cria embates relacionados com referências cruzadas
    embates = [
        {
            "titulo": "Arquitetura Base",
            "tipo": "tecnico",
            "contexto": "Definição da arquitetura base",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": "Proposta inicial de arquitetura",
                    "data": datetime.now().isoformat()
                }
            ],
            "decisao": "Usar arquitetura em camadas",
            "razao": "Melhor separação de responsabilidades",
            "arquivo": "embate_arquitetura.json",
            "referencias": []  # Primeiro embate, sem referências
        },
        {
            "titulo": "Padrão de API",
            "tipo": "tecnico",
            "contexto": "Definição do padrão de API",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": "Considerando a arquitetura definida anteriormente",
                    "data": datetime.now().isoformat(),
                    "referencias": ["embate_arquitetura.json"]
                }
            ],
            "decisao": "Usar REST com HATEOAS",
            "razao": "Compatível com a arquitetura em camadas",
            "arquivo": "embate_api.json",
            "referencias": ["embate_arquitetura.json"]
        },
        {
            "titulo": "Implementação de Cache",
            "tipo": "tecnico",
            "contexto": "Estratégia de cache",
            "status": "resolvido",
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "AI",
                    "tipo": "tecnico",
                    "conteudo": "Baseado na API REST definida",
                    "data": datetime.now().isoformat(),
                    "referencias": ["embate_api.json"]
                }
            ],
            "decisao": "Usar cache distribuído",
            "razao": "Necessário para escalabilidade da API",
            "arquivo": "embate_cache.json",
            "referencias": ["embate_api.json", "embate_arquitetura.json"]
        }
    ]
    
    # Salva os embates
    for embate in embates:
        with open(embates_dir / embate["arquivo"], "w") as f:
            json.dump(embate, f)
    
    condensador = CondensadorEmbates(
        dir_embates=str(embates_dir),
        dir_regras=str(regras_dir),
        min_embates_tema=1
    )
    
    # Processa e gera regras
    arquivos_gerados = await condensador.processar()
    
    # Verifica se as regras foram geradas
    assert len(arquivos_gerados) == 1
    
    # Verifica conteúdo do arquivo
    conteudo = arquivos_gerados[0].read_text()
    
    # Verifica ordem das decisões (deve seguir a ordem de dependência)
    decisoes_pos = {
        decisao: conteudo.index(decisao)
        for decisao in [
            "Usar arquitetura em camadas",
            "Usar REST com HATEOAS",
            "Usar cache distribuído"
        ]
    }
    
    # Verifica se a ordem está correta
    assert decisoes_pos["Usar arquitetura em camadas"] < decisoes_pos["Usar REST com HATEOAS"]
    assert decisoes_pos["Usar REST com HATEOAS"] < decisoes_pos["Usar cache distribuído"]
    
    # Verifica links entre as decisões
    assert re.search(r"\[Arquitetura Base\]\(#arquitetura-base\)", conteudo)
    assert re.search(r"\[Padrão de API\]\(#padrão-de-api\)", conteudo)
    
    # Verifica menções às referências
    assert "Baseado na decisão de [Arquitetura Base]" in conteudo
    assert "Relacionado à decisão de [Padrão de API]" in conteudo
    
    # Verifica seção de relacionamentos
    assert "## Relacionamentos entre Decisões" in conteudo
    assert "- Arquitetura Base → Padrão de API" in conteudo
    assert "- Padrão de API → Implementação de Cache" in conteudo
    
    # Verifica metadados de rastreabilidade
    assert "Decisões relacionadas:" in conteudo
    assert "Decisões dependentes:" in conteudo 