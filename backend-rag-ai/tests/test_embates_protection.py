import pytest
from datetime import datetime
from backend_rag_ai_py.monitoring.embates_protection_manager import EmbatesProtectionManager

@pytest.fixture
def protection_manager():
    return EmbatesProtectionManager()

def test_embate_protection_basic(protection_manager):
    """Testa proteções básicas do sistema"""
    embate_incompleto = {
        'titulo': 'Teste Básico'
    }
    
    protected = protection_manager.process_embate(embate_incompleto)
    
    # Verifica campos protegidos
    assert 'data_inicio' in protected
    assert 'status' in protected
    assert 'metadata' in protected
    assert 'argumentos' in protected
    assert 'tipo' in protected
    assert 'contexto' in protected
    
    # Verifica valores padrão
    assert protected['status'] == 'aberto'
    assert protected['tipo'] == 'tecnico'
    assert isinstance(protected['argumentos'], list)
    
def test_embate_validation_errors(protection_manager):
    """Testa validação de erros críticos"""
    embate_invalido = {
        'titulo': 'Teste Inválido',
        'tools_count': 4,  # Excede limite
        'data_inicio': 'data-invalida'
    }
    
    with pytest.raises(ValueError) as exc_info:
        protection_manager.process_embate(embate_invalido)
    
    assert 'Erros críticos encontrados' in str(exc_info.value)
    
def test_embate_metadata_validation(protection_manager):
    """Testa validação de metadata"""
    embate_metadata_invalida = {
        'titulo': 'Teste Metadata',
        'metadata': {
            'impacto': 'invalido',
            'prioridade': 'baixa',
            'tags': 'não-é-lista'
        }
    }
    
    validation = protection_manager.validate_only(embate_metadata_invalida)
    assert any(w['rule_name'] == 'validacao_metadata' for w in validation['warnings'])
    
def test_embate_date_validation(protection_manager):
    """Testa validação de datas"""
    data_futura = datetime.now().isoformat()
    data_passada = datetime(2020, 1, 1).isoformat()
    
    embate_datas_invalidas = {
        'titulo': 'Teste Datas',
        'data_inicio': data_futura,
        'data_fim': data_passada
    }
    
    validation = protection_manager.validate_only(embate_datas_invalidas)
    assert any(e['rule_name'] == 'consistencia_datas' for e in validation['errors'])
    
def test_embate_tools_limit(protection_manager):
    """Testa limite de ferramentas"""
    embate_limite = {
        'titulo': 'Teste Limite',
        'tools_count': 3
    }
    
    # Deve passar com 3 ferramentas
    protected = protection_manager.process_embate(embate_limite)
    assert protected['tools_count'] == 3
    
    # Deve falhar com 4 ferramentas
    embate_limite['tools_count'] = 4
    with pytest.raises(ValueError) as exc_info:
        protection_manager.process_embate(embate_limite)
    
    assert 'Limite de 3 ferramentas excedido' in str(exc_info.value)
    
def test_embate_preventive_warning(protection_manager):
    """Testa aviso preventivo"""
    embate_sem_aviso = {
        'titulo': 'Teste Aviso',
        'tools_count': 2,
        'warnings': []
    }
    
    validation = protection_manager.validate_only(embate_sem_aviso)
    assert any(w['rule_name'] == 'aviso_preventivo' for w in validation['warnings'])
    
def test_embate_complete_valid(protection_manager):
    """Testa embate completamente válido"""
    embate_valido = {
        'titulo': 'Teste Válido',
        'tipo': 'tecnico',
        'contexto': 'Contexto de teste',
        'status': 'aberto',
        'data_inicio': datetime.now().isoformat(),
        'argumentos': [],
        'metadata': {
            'impacto': 'médio',
            'prioridade': 'alta',
            'tags': ['teste', 'validação']
        },
        'tools_count': 2,
        'warnings': ['Aviso preventivo ativo']
    }
    
    # Não deve levantar exceções
    protected = protection_manager.process_embate(embate_valido)
    assert protection_manager.is_valid(protected)
    
    # Validação não deve ter erros
    validation = protection_manager.validate_only(protected)
    assert len(validation['errors']) == 0 