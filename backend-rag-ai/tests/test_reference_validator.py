import pytest
import json
import os
from pathlib import Path
from ..validators.reference_validator import ReferenceValidator

@pytest.fixture
def temp_embates_dir(tmp_path):
    """Fixture que cria diretório temporário com embates"""
    embates_dir = tmp_path / "embates"
    embates_dir.mkdir()
    return str(embates_dir)

@pytest.fixture
def validator(temp_embates_dir):
    """Fixture que cria validador"""
    return ReferenceValidator(temp_embates_dir)

@pytest.fixture
def sample_embates(temp_embates_dir):
    """Fixture que cria embates de exemplo"""
    embates = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "titulo": "Embate 1",
            "tipo": "feature",
            "status": "aberto",
            "contexto": "Contexto do embate 1",
            "argumentos": []
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "titulo": "Embate 2",
            "tipo": "feature",
            "status": "em_andamento",
            "contexto": "Referência ao #11111111-1111-1111-1111-111111111111",
            "argumentos": []
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "titulo": "Embate 3",
            "tipo": "feature",
            "status": "fechado",
            "contexto": "Embate fechado",
            "argumentos": []
        }
    ]
    
    # Salva embates
    for embate in embates:
        file_path = Path(temp_embates_dir) / f"{embate['id']}.json"
        with open(file_path, 'w') as f:
            json.dump(embate, f)
    
    return embates

def test_extract_references(validator):
    """Testa extração de referências"""
    # Referência com #
    refs = validator._extract_references(
        "Referência ao #11111111-1111-1111-1111-111111111111"
    )
    assert "11111111-1111-1111-1111-111111111111" in refs
    
    # Referência com []
    refs = validator._extract_references(
        "Referência ao [11111111-1111-1111-1111-111111111111]"
    )
    assert "11111111-1111-1111-1111-111111111111" in refs
    
    # Referência com ()
    refs = validator._extract_references(
        "Referência ao (11111111-1111-1111-1111-111111111111)"
    )
    assert "11111111-1111-1111-1111-111111111111" in refs
    
    # Múltiplas referências
    refs = validator._extract_references(
        "Refs: #111 [222] (333) #444"
    )
    assert len(refs) == 0  # IDs inválidos são ignorados
    
    # Sem referências
    refs = validator._extract_references("Texto sem referências")
    assert not refs

def test_get_references(validator, sample_embates):
    """Testa obtenção de referências"""
    # Embate com referência
    refs = validator.get_references(sample_embates[1])
    assert "11111111-1111-1111-1111-111111111111" in refs
    
    # Embate sem referência
    refs = validator.get_references(sample_embates[0])
    assert not refs
    
    # Embate com referência em argumento
    embate = sample_embates[0].copy()
    embate['argumentos'] = [{
        "tipo": "analise",
        "conteudo": "Ref: #22222222-2222-2222-2222-222222222222"
    }]
    refs = validator.get_references(embate)
    assert "22222222-2222-2222-2222-222222222222" in refs

def test_get_reverse_references(validator, sample_embates):
    """Testa obtenção de referências reversas"""
    # Embate referenciado
    refs = validator.get_reverse_references(
        "11111111-1111-1111-1111-111111111111"
    )
    assert len(refs) == 1
    assert refs[0]['id'] == "22222222-2222-2222-2222-222222222222"
    
    # Embate não referenciado
    refs = validator.get_reverse_references(
        "33333333-3333-3333-3333-333333333333"
    )
    assert not refs
    
    # ID inexistente
    refs = validator.get_reverse_references("invalid")
    assert not refs

def test_validate_references(validator, sample_embates):
    """Testa validação de referências"""
    # Referência válida
    errors = validator.validate_references(sample_embates[1])
    assert not errors
    
    # Referência não encontrada
    embate = sample_embates[0].copy()
    embate['contexto'] = "Ref: #99999999-9999-9999-9999-999999999999"
    errors = validator.validate_references(embate)
    assert errors
    assert any("não encontrada" in error for error in errors)
    
    # Referência cíclica
    embate1 = sample_embates[0].copy()
    embate1['contexto'] = "Ref: #22222222-2222-2222-2222-222222222222"
    embate2 = sample_embates[1].copy()
    embate2['contexto'] = "Ref: #11111111-1111-1111-1111-111111111111"
    
    errors = validator.validate_references(embate1)
    assert errors
    assert any("cíclica" in error for error in errors)

def test_check_orphaned_references(validator, sample_embates):
    """Testa verificação de referências órfãs"""
    # Sistema sem problemas
    problems = validator.check_orphaned_references()
    assert not problems
    
    # Referência não encontrada
    embate = sample_embates[0].copy()
    embate['contexto'] = "Ref: #99999999-9999-9999-9999-999999999999"
    file_path = Path(validator.embates_dir) / f"{embate['id']}.json"
    with open(file_path, 'w') as f:
        json.dump(embate, f)
    
    problems = validator.check_orphaned_references()
    assert problems
    assert any(p['tipo'] == 'referencia_nao_encontrada' for p in problems)
    
    # Ciclo de referências
    embate1 = sample_embates[0].copy()
    embate1['contexto'] = "Ref: #22222222-2222-2222-2222-222222222222"
    embate2 = sample_embates[1].copy()
    embate2['contexto'] = "Ref: #11111111-1111-1111-1111-111111111111"
    
    file_path = Path(validator.embates_dir) / f"{embate1['id']}.json"
    with open(file_path, 'w') as f:
        json.dump(embate1, f)
    
    file_path = Path(validator.embates_dir) / f"{embate2['id']}.json"
    with open(file_path, 'w') as f:
        json.dump(embate2, f)
    
    problems = validator.check_orphaned_references()
    assert problems
    assert any(p['tipo'] == 'ciclo_detectado' for p in problems)

def test_get_reference_graph(validator, sample_embates):
    """Testa geração de grafo de referências"""
    # Grafo simples
    graph = validator.get_reference_graph(
        "22222222-2222-2222-2222-222222222222"
    )
    assert len(graph['nodes']) == 2
    assert len(graph['edges']) == 1
    
    # Verifica nós
    node_ids = {node['id'] for node in graph['nodes']}
    assert "11111111-1111-1111-1111-111111111111" in node_ids
    assert "22222222-2222-2222-2222-222222222222" in node_ids
    
    # Verifica aresta
    edge = graph['edges'][0]
    assert edge['source'] == "22222222-2222-2222-2222-222222222222"
    assert edge['target'] == "11111111-1111-1111-1111-111111111111"
    
    # ID inexistente
    graph = validator.get_reference_graph("invalid")
    assert not graph['nodes']
    assert not graph['edges'] 