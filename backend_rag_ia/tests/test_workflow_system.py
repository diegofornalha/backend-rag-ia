import pytest
from datetime import datetime, timedelta
from ..templates.embate_templates import EmbateTemplates
from ..validators.workflow_validator import WorkflowValidator
from ..metrics.workflow_metrics import WorkflowMetrics

@pytest.fixture
def templates():
    return EmbateTemplates()

@pytest.fixture
def validator():
    return WorkflowValidator()

@pytest.fixture
def metrics():
    return WorkflowMetrics()

def test_feature_template(templates):
    """Testa template de feature"""
    embate = EmbateTemplates.create_feature_embate(
        titulo="Test Feature",
        contexto="Test Context",
        autor="test_user"
    )
    
    assert embate['titulo'] == "Test Feature"
    assert embate['tipo'] == "feature"
    assert len(embate['argumentos']) == 1
    assert embate['argumentos'][0]['tipo'] == "analise"

def test_bug_template(templates):
    """Testa template de bug"""
    embate = EmbateTemplates.create_bug_embate(
        titulo="Test Bug",
        descricao="Test Description",
        autor="test_user",
        severidade="alta"
    )
    
    assert embate['tipo'] == "bug"
    assert embate['metadata']['prioridade'] == "alta"
    assert 'bug' in embate['metadata']['tags']

def test_process_template(templates):
    """Testa template de processo"""
    embate = EmbateTemplates.create_process_embate(
        titulo="Test Process",
        contexto="Test Context",
        autor="test_user",
        area="workflow"
    )
    
    assert embate['tipo'] == "processo"
    assert 'workflow' in embate['metadata']['tags']

def test_tech_debt_template(templates):
    """Testa template de dívida técnica"""
    embate = EmbateTemplates.create_tech_debt_embate(
        titulo="Test Tech Debt",
        descricao="Test Description",
        autor="test_user",
        componente="database"
    )
    
    assert embate['tipo'] == "tech_debt"
    assert 'database' in embate['metadata']['tags']

def test_sequence_validation(validator):
    """Testa validação de sequência"""
    embate = {
        'tipo': 'feature',
        'argumentos': [
            {'tipo': 'analise'},
            {'tipo': 'solucao'},
            {'tipo': 'implementacao'}
        ]
    }
    
    errors = validator.validate_sequence(embate)
    assert len(errors) == 0
    
    # Sequência inválida
    embate['argumentos'].append({'tipo': 'invalid'})
    errors = validator.validate_sequence(embate)
    assert len(errors) > 0

def test_state_transition(validator):
    """Testa validação de transição de estado"""
    # Transição válida
    error = validator.validate_state_transition('aberto', 'em_andamento')
    assert error is None
    
    # Transição inválida
    error = validator.validate_state_transition('aberto', 'invalido')
    assert error is not None

def test_metadata_validation(validator):
    """Testa validação de metadata"""
    embate = {
        'metadata': {
            'impacto': 'alto',
            'prioridade': 'alta',
            'tags': ['test']
        }
    }
    
    errors = validator.validate_metadata(embate)
    assert len(errors) == 0
    
    # Metadata inválida
    embate['metadata']['impacto'] = 'invalido'
    errors = validator.validate_metadata(embate)
    assert len(errors) > 0

def test_metrics_recording(metrics):
    """Testa registro de métricas"""
    embate_id = 'test_embate'
    
    # Registra mudanças de estado
    metrics.record_state_change(embate_id, 'aberto', 'em_andamento')
    metrics.record_state_change(embate_id, 'em_andamento', 'fechado')
    
    # Verifica cycle time
    cycle_time = metrics.get_cycle_time(embate_id)
    assert cycle_time is not None
    assert isinstance(cycle_time, timedelta)
    
    # Verifica estatísticas
    stats = metrics.get_statistics()
    assert stats['total_embates'] >= 1
    assert stats['state_changes'] >= 2

def test_state_duration(metrics):
    """Testa cálculo de duração em estados"""
    embate_id = 'test_duration'
    
    # Registra estados
    metrics.record_state_change(embate_id, 'aberto', 'em_andamento')
    
    # Espera um pouco
    import time
    time.sleep(0.1)
    
    # Muda estado
    metrics.record_state_change(embate_id, 'em_andamento', 'fechado')
    
    # Verifica duração
    duration = metrics.get_state_duration(embate_id, 'em_andamento')
    assert duration > timedelta(0)

def test_workflow_integration(templates, validator, metrics):
    """Testa integração completa do workflow"""
    # Cria embate
    embate = EmbateTemplates.create_feature_embate(
        titulo="Integration Test",
        contexto="Testing workflow integration",
        autor="test_user"
    )
    
    # Valida
    validation = validator.validate_embate(embate)
    assert len(validation['sequence']) == 0
    assert len(validation['metadata']) == 0
    
    # Registra métricas
    embate_id = 'integration_test'
    metrics.record_state_change(embate_id, 'aberto', 'em_andamento')
    metrics.record_operation(embate_id, 'create')
    
    # Verifica estatísticas
    stats = metrics.get_statistics()
    assert stats['total_embates'] >= 1
    assert 'operation_create' in stats['operations'] 