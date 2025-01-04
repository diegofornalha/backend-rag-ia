import pytest
from datetime import datetime
import json
import os
from ..validators.schema_validator import SchemaValidator

@pytest.fixture
def valid_feature_embate():
    """Fixture com embate de feature válido"""
    return {
        "titulo": "Feature Test",
        "tipo": "feature",
        "contexto": "Test Context",
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [{
            "autor": "test_user",
            "tipo": "analise",
            "conteudo": "Test Content",
            "data": datetime.now().isoformat()
        }],
        "metadata": {
            "impacto": "médio",
            "prioridade": "média",
            "tags": ["test"]
        }
    }

@pytest.fixture
def valid_bug_embate():
    """Fixture com embate de bug válido"""
    return {
        "titulo": "Bug Test",
        "tipo": "bug",
        "descricao": "Test Description",
        "severidade": "média",
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [{
            "autor": "test_user",
            "tipo": "analise",
            "conteudo": "Test Content",
            "data": datetime.now().isoformat()
        }],
        "metadata": {
            "impacto": "médio",
            "prioridade": "média",
            "tags": ["test"]
        }
    }

def test_validate_date_format():
    """Testa validação de formato de data"""
    # Data válida
    assert SchemaValidator.validate_date_format(datetime.now().isoformat())
    
    # Data inválida
    assert not SchemaValidator.validate_date_format("invalid-date")
    assert not SchemaValidator.validate_date_format("2024-01-04")  # Falta hora

def test_validate_feature_embate(valid_feature_embate):
    """Testa validação de embate de feature"""
    # Embate válido
    errors = SchemaValidator.validate_embate(valid_feature_embate)
    assert not errors
    
    # Sem título
    invalid = valid_feature_embate.copy()
    invalid.pop('titulo')
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('titulo' in error.lower() for error in errors)
    
    # Tipo inválido
    invalid = valid_feature_embate.copy()
    invalid['tipo'] = 'invalid'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('tipo' in error.lower() for error in errors)
    
    # Status inválido
    invalid = valid_feature_embate.copy()
    invalid['status'] = 'invalid'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('status' in error.lower() for error in errors)

def test_validate_bug_embate(valid_bug_embate):
    """Testa validação de embate de bug"""
    # Embate válido
    errors = SchemaValidator.validate_embate(valid_bug_embate)
    assert not errors
    
    # Sem severidade
    invalid = valid_bug_embate.copy()
    invalid.pop('severidade')
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('severidade' in error.lower() for error in errors)
    
    # Severidade inválida
    invalid = valid_bug_embate.copy()
    invalid['severidade'] = 'invalid'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('severidade' in error.lower() for error in errors)

def test_validate_metadata(valid_feature_embate):
    """Testa validação de metadata"""
    # Metadata válida
    errors = SchemaValidator.validate_embate(valid_feature_embate)
    assert not errors
    
    # Sem impacto
    invalid = valid_feature_embate.copy()
    invalid['metadata'].pop('impacto')
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('impacto' in error.lower() for error in errors)
    
    # Impacto inválido
    invalid = valid_feature_embate.copy()
    invalid['metadata']['impacto'] = 'invalid'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('impacto' in error.lower() for error in errors)
    
    # Tags vazias
    invalid = valid_feature_embate.copy()
    invalid['metadata']['tags'] = []
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('tags' in error.lower() for error in errors)

def test_validate_argumentos(valid_feature_embate):
    """Testa validação de argumentos"""
    # Argumentos válidos
    errors = SchemaValidator.validate_embate(valid_feature_embate)
    assert not errors
    
    # Sem argumentos
    invalid = valid_feature_embate.copy()
    invalid['argumentos'] = []
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('argumentos' in error.lower() for error in errors)
    
    # Tipo de argumento inválido
    invalid = valid_feature_embate.copy()
    invalid['argumentos'][0]['tipo'] = 'invalid'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('tipo' in error.lower() for error in errors)
    
    # Data inválida
    invalid = valid_feature_embate.copy()
    invalid['argumentos'][0]['data'] = 'invalid-date'
    errors = SchemaValidator.validate_embate(invalid)
    assert errors
    assert any('data' in error.lower() for error in errors)

def test_validate_json_file(valid_feature_embate, tmp_path):
    """Testa validação de arquivo JSON"""
    # Cria arquivo temporário
    file_path = tmp_path / "test_embate.json"
    with open(file_path, 'w') as f:
        json.dump(valid_feature_embate, f)
    
    # Arquivo válido
    errors = SchemaValidator.validate_json_file(str(file_path))
    assert not errors
    
    # Arquivo inválido
    with open(file_path, 'w') as f:
        f.write("invalid json")
    
    errors = SchemaValidator.validate_json_file(str(file_path))
    assert errors
    assert any('json' in error.lower() for error in errors)
    
    # Arquivo não existe
    errors = SchemaValidator.validate_json_file("non_existent.json")
    assert errors
    assert any('arquivo' in error.lower() for error in errors)

def test_sanitize_embate():
    """Testa sanitização de embate"""
    # Embate com data inválida
    embate = {
        "titulo": "Test",
        "tipo": "feature",
        "contexto": "Test",
        "status": "aberto",
        "data_inicio": "invalid-date",
        "argumentos": [{
            "autor": "test_user",
            "tipo": "analise",
            "conteudo": "Test",
            "data": "invalid-date"
        }],
        "metadata": {
            "impacto": "médio",
            "prioridade": "média",
            "tags": ["test"]
        }
    }
    
    sanitized = SchemaValidator.sanitize_embate(embate)
    
    # Verifica se as datas foram corrigidas
    assert SchemaValidator.validate_date_format(sanitized['data_inicio'])
    assert SchemaValidator.validate_date_format(sanitized['argumentos'][0]['data'])
    
    # Embate sem metadata
    embate.pop('metadata')
    sanitized = SchemaValidator.sanitize_embate(embate)
    
    # Verifica se metadata foi adicionada
    assert 'metadata' in sanitized
    assert 'impacto' in sanitized['metadata']
    assert 'prioridade' in sanitized['metadata']
    assert 'tags' in sanitized['metadata'] 