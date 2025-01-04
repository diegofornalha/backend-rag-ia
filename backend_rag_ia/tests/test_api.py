<<<<<<< Updated upstream
"""Implementa testes para a API do backend_rag_ia.

Este módulo contém testes para os endpoints da API, incluindo
operações com documentos, embeddings, monitoramento e operações em lote.
"""

=======
>>>>>>> Stashed changes
from datetime import datetime
from unittest.mock import patch

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Fixtures
@pytest.fixture
def mock_supabase():
<<<<<<< Updated upstream
    """Cria um mock do cliente Supabase para testes."""
=======
>>>>>>> Stashed changes
    with patch('app.main.supabase') as mock:
        yield mock

@pytest.fixture
def sample_document():
<<<<<<< Updated upstream
    """Retorna um documento de exemplo para testes.

    Returns
    -------
    dict
        Documento com título, conteúdo e metadados.

    """
=======
>>>>>>> Stashed changes
    return {
        'titulo': 'Teste',
        'conteudo': {'texto': 'Conteúdo de teste'},
        'metadata': {'autor': 'Teste'}
    }

@pytest.fixture
def sample_document_response(sample_document):
<<<<<<< Updated upstream
    """Retorna uma resposta de documento de exemplo para testes.

    Parameters
    ----------
    sample_document : dict
        Documento base para gerar a resposta.

    Returns
    -------
    dict
        Resposta completa de documento com ID e timestamps.

    """
=======
>>>>>>> Stashed changes
    return {
        'id': '123',
        'titulo': sample_document['titulo'],
        'conteudo': sample_document['conteudo'],
        'metadata': sample_document['metadata'],
        'content_hash': 'hash123',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

# Testes de Documentos
def test_create_document_success(mock_supabase, sample_document, sample_document_response):
<<<<<<< Updated upstream
    """Testa a criação bem-sucedida de um documento.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.
    sample_document : dict
        Documento de exemplo para criar.
    sample_document_response : dict
        Resposta esperada após a criação.

    """
=======
>>>>>>> Stashed changes
    # Mock das chamadas ao Supabase
    mock_supabase.rpc().execute.return_value.data = None
    mock_supabase.table().insert().execute.return_value.data = [sample_document_response]
    mock_supabase.rpc().execute.return_value.data = None

    response = client.post('/api/v1/documents', json=sample_document)

    assert response.status_code == 200
    assert response.json()['id'] == '123'
    assert response.json()['titulo'] == sample_document['titulo']

def test_create_document_duplicate(mock_supabase, sample_document):
<<<<<<< Updated upstream
    """Testa a tentativa de criar um documento duplicado.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.
    sample_document : dict
        Documento de exemplo para tentar criar.

    """
=======
>>>>>>> Stashed changes
    # Mock para simular documento duplicado
    mock_supabase.rpc().execute.return_value.data = [{'exists': True}]

    response = client.post('/api/v1/documents', json=sample_document)

    assert response.status_code == 409
    assert response.json()['detail'] == 'Documento duplicado'

def test_get_document_success(mock_supabase, sample_document_response):
<<<<<<< Updated upstream
    """Testa a busca bem-sucedida de um documento.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.
    sample_document_response : dict
        Resposta esperada da busca.

    """
=======
>>>>>>> Stashed changes
    # Mock para busca de documento
    mock_supabase.table().select().eq().execute.return_value.data = [sample_document_response]
    mock_supabase.table().select().eq().execute.return_value.data = []

    response = client.get('/api/v1/documents/123')

    assert response.status_code == 200
    assert response.json()['id'] == '123'

def test_get_document_not_found(mock_supabase):
<<<<<<< Updated upstream
    """Testa a busca de um documento inexistente.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.

    """
=======
>>>>>>> Stashed changes
    # Mock para documento não encontrado
    mock_supabase.table().select().eq().execute.return_value.data = []

    response = client.get('/api/v1/documents/123')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Documento não encontrado'

# Testes de Embeddings
def test_generate_embedding_success():
<<<<<<< Updated upstream
    """Testa a geração bem-sucedida de um embedding."""
=======
>>>>>>> Stashed changes
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'embedding': [0.1, 0.2, 0.3]}

        response = client.post('/api/v1/embeddings', json={'text': 'teste'})

        assert response.status_code == 200
        assert len(response.json()) == 3

def test_sync_document_embedding_success(mock_supabase, sample_document_response):
<<<<<<< Updated upstream
    """Testa a sincronização bem-sucedida de embedding de documento.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.
    sample_document_response : dict
        Resposta de documento para sincronizar.

    """
=======
>>>>>>> Stashed changes
    # Mock para busca de documento
    mock_supabase.table().select().eq().execute.return_value.data = [sample_document_response]

    # Mock para chamada da API
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'embedding': [0.1, 0.2, 0.3]}

        # Mock para inserção do embedding
        mock_supabase.table().select().eq().execute.return_value.data = []
        mock_supabase.table().insert().execute.return_value.data = [{
            'id': '456',
            'document_id': '123',
            'embedding': [0.1, 0.2, 0.3],
            'content_hash': 'hash123',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }]

        response = client.post('/api/v1/documents/123/embedding')

        assert response.status_code == 200
        assert response.json()['document_id'] == '123'

# Testes de Monitoramento
def test_get_statistics_success(mock_supabase):
<<<<<<< Updated upstream
    """Testa a obtenção bem-sucedida de estatísticas.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.

    """
=======
>>>>>>> Stashed changes
    stats_data = {
        'id': '789',
        'total_documents': 10,
        'documents_with_embeddings': 8,
        'documents_without_embeddings': 2,
        'total_embeddings': 8,
        'created_at': datetime.utcnow().isoformat()
    }

    mock_supabase.table().select().order().limit().execute.return_value.data = [stats_data]

    response = client.get('/api/v1/statistics')

    assert response.status_code == 200
    assert response.json()['total_documents'] == 10

def test_health_check_success(mock_supabase):
<<<<<<< Updated upstream
    """Testa a verificação bem-sucedida de saúde da API.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.

    """
=======
>>>>>>> Stashed changes
    mock_supabase.table().select().head().execute.return_value.data = True

    response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

# Testes de Operações em Lote
def test_batch_upload_success(mock_supabase, sample_document):
<<<<<<< Updated upstream
    """Testa o upload em lote bem-sucedido de documentos.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.
    sample_document : dict
        Documento de exemplo para upload.

    """
=======
>>>>>>> Stashed changes
    batch_data = {
        'id': '999',
        'status': 'processing',
        'operation_type': 'batch_upload',
        'total_items': 1,
        'processed_items': 0,
        'errors': [],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    mock_supabase.table().insert().execute.return_value.data = [batch_data]

    response = client.post('/api/v1/documents/batch', json=[sample_document])

    assert response.status_code == 200
    assert response.json()['status'] == 'processing'

def test_get_batch_status_success(mock_supabase):
<<<<<<< Updated upstream
    """Testa a obtenção bem-sucedida do status de uma operação em lote.

    Parameters
    ----------
    mock_supabase : MagicMock
        Mock do cliente Supabase.

    """
=======
>>>>>>> Stashed changes
    batch_data = {
        'id': '999',
        'status': 'completed',
        'operation_type': 'batch_upload',
        'total_items': 1,
        'processed_items': 1,
        'errors': [],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    mock_supabase.table().select().eq().execute.return_value.data = [batch_data]

    response = client.get('/api/v1/documents/batch/999')

    assert response.status_code == 200
    assert response.json()['status'] == 'completed'
