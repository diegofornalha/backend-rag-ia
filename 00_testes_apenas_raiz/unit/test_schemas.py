"""Testes unitários para validação dos schemas Pydantic."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend_rag_ia.cli.c_embates_saudaveis import Argumento, Embate


# Testes para o schema Argumento
def test_argumento_valid():
    """Testa criação de Argumento com dados válidos."""
    data = {
        "autor": "AI",
        "conteudo": "Argumento de teste",
        "tipo": "tecnico",
        "data": datetime.now()
    }
    argumento = Argumento(**data)
    assert argumento.autor == data["autor"]
    assert argumento.conteudo == data["conteudo"]
    assert argumento.tipo == data["tipo"]
    assert isinstance(argumento.data, datetime)

def test_argumento_invalid_tipo():
    """Testa validação do campo tipo do Argumento."""
    with pytest.raises(ValidationError) as exc_info:
        Argumento(
            autor="AI",
            conteudo="Teste",
            tipo="invalido",  # Tipo inválido
            data=datetime.now()
        )
    assert "tipo" in str(exc_info.value)
    assert "pattern" in str(exc_info.value)

def test_argumento_missing_fields():
    """Testa validação de campos obrigatórios do Argumento."""
    with pytest.raises(ValidationError) as exc_info:
        Argumento(autor="AI")  # Faltam campos obrigatórios
    assert "conteudo" in str(exc_info.value)
    assert "tipo" in str(exc_info.value)
    assert "data" in str(exc_info.value)

# Testes para o schema Embate
def test_embate_valid():
    """Testa criação de Embate com dados válidos."""
    data = {
        "titulo": "Teste",
        "tipo": "tecnico",
        "contexto": "Contexto de teste",
        "status": "aberto",
        "data_inicio": datetime.now(),
        "argumentos": [],
        "decisao": None,
        "razao": None,
        "arquivo": "embate_test.json"
    }
    embate = Embate(**data)
    assert embate.titulo == data["titulo"]
    assert embate.tipo == data["tipo"]
    assert embate.contexto == data["contexto"]
    assert embate.status == data["status"]
    assert isinstance(embate.data_inicio, datetime)
    assert embate.argumentos == []
    assert embate.decisao is None
    assert embate.razao is None
    assert embate.arquivo == data["arquivo"]

def test_embate_with_argumentos():
    """Testa criação de Embate com argumentos."""
    argumento = Argumento(
        autor="AI",
        conteudo="Teste",
        tipo="tecnico",
        data=datetime.now()
    )
    
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="Contexto",
        status="aberto",
        data_inicio=datetime.now(),
        argumentos=[argumento],
        decisao=None,
        razao=None,
        arquivo="test.json"
    )
    
    assert len(embate.argumentos) == 1
    assert isinstance(embate.argumentos[0], Argumento)
    assert embate.argumentos[0].autor == "AI"

def test_embate_invalid_tipo():
    """Testa validação do campo tipo do Embate."""
    with pytest.raises(ValidationError) as exc_info:
        Embate(
            titulo="Teste",
            tipo="invalido",  # Tipo inválido
            contexto="Contexto",
            status="aberto",
            data_inicio=datetime.now(),
            argumentos=[],
            decisao=None,
            razao=None,
            arquivo="test.json"
        )
    assert "tipo" in str(exc_info.value)
    assert "pattern" in str(exc_info.value)

def test_embate_invalid_status():
    """Testa validação do campo status do Embate."""
    with pytest.raises(ValidationError) as exc_info:
        Embate(
            titulo="Teste",
            tipo="tecnico",
            contexto="Contexto",
            status="invalido",  # Status inválido
            data_inicio=datetime.now(),
            argumentos=[],
            decisao=None,
            razao=None,
            arquivo="test.json"
        )
    assert "status" in str(exc_info.value)
    assert "pattern" in str(exc_info.value)

def test_embate_missing_fields():
    """Testa validação de campos obrigatórios do Embate."""
    with pytest.raises(ValidationError) as exc_info:
        Embate(titulo="Teste")  # Faltam campos obrigatórios
    assert "tipo" in str(exc_info.value)
    assert "contexto" in str(exc_info.value)
    assert "status" in str(exc_info.value)
    assert "data_inicio" in str(exc_info.value)

def test_embate_invalid_argumentos():
    """Testa validação da lista de argumentos do Embate."""
    with pytest.raises(ValidationError) as exc_info:
        Embate(
            titulo="Teste",
            tipo="tecnico",
            contexto="Contexto",
            status="aberto",
            data_inicio=datetime.now(),
            argumentos=[{"autor": "AI"}],  # Argumento inválido
            decisao=None,
            razao=None,
            arquivo="test.json"
        )
    assert "argumentos" in str(exc_info.value)

def test_embate_resolved_without_decision():
    """Testa validação de embate resolvido sem decisão."""
    with pytest.raises(ValidationError) as exc_info:
        Embate(
            titulo="Teste",
            tipo="tecnico",
            contexto="Contexto",
            status="resolvido",  # Resolvido mas sem decisão
            data_inicio=datetime.now(),
            argumentos=[],
            decisao=None,  # Deveria ter uma decisão
            razao=None,
            arquivo="test.json"
        )
    assert "decisao" in str(exc_info.value) 