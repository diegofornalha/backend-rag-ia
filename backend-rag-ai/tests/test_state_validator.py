import pytest
from datetime import datetime, timezone, timedelta
from ..validators.state_validator import StateValidator

@pytest.fixture
def sample_embate():
    """Fixture com embate de exemplo"""
    return {
        "titulo": "Test Embate",
        "tipo": "feature",
        "status": "aberto",
        "data_inicio": datetime.now(timezone.utc).isoformat(),
        "argumentos": [
            {
                "autor": "test_user",
                "tipo": "analise",
                "conteudo": "Test Analysis",
                "data": datetime.now(timezone.utc).isoformat()
            }
        ],
        "metadata": {
            "impacto": "médio",
            "prioridade": "média",
            "tags": ["test"]
        }
    }

def test_validate_state():
    """Testa validação de estados"""
    # Estados válidos
    assert StateValidator.validate_state("aberto")
    assert StateValidator.validate_state("em_andamento")
    assert StateValidator.validate_state("bloqueado")
    assert StateValidator.validate_state("fechado")
    
    # Estados inválidos
    assert not StateValidator.validate_state("invalid")
    assert not StateValidator.validate_state("")
    assert not StateValidator.validate_state("ABERTO")

def test_validate_transition():
    """Testa validação de transições"""
    # Transições válidas
    assert StateValidator.validate_transition("aberto", "em_andamento")
    assert StateValidator.validate_transition("em_andamento", "bloqueado")
    assert StateValidator.validate_transition("bloqueado", "em_andamento")
    assert StateValidator.validate_transition("em_andamento", "fechado")
    
    # Transições inválidas
    assert not StateValidator.validate_transition("fechado", "em_andamento")
    assert not StateValidator.validate_transition("bloqueado", "aberto")
    assert not StateValidator.validate_transition("invalid", "em_andamento")
    assert not StateValidator.validate_transition("aberto", "invalid")

def test_get_valid_transitions():
    """Testa obtenção de transições válidas"""
    # Estado aberto
    transitions = StateValidator.get_valid_transitions("aberto")
    assert "em_andamento" in transitions
    assert "bloqueado" in transitions
    assert "fechado" in transitions
    
    # Estado em_andamento
    transitions = StateValidator.get_valid_transitions("em_andamento")
    assert "bloqueado" in transitions
    assert "fechado" in transitions
    assert "aberto" not in transitions
    
    # Estado fechado
    transitions = StateValidator.get_valid_transitions("fechado")
    assert not transitions  # Conjunto vazio
    
    # Estado inválido
    transitions = StateValidator.get_valid_transitions("invalid")
    assert not transitions  # Conjunto vazio

def test_validate_requirements():
    """Testa validação de requisitos"""
    # Argumentos válidos para em_andamento
    arguments = [
        {
            "autor": "test_user",
            "tipo": "analise",
            "conteudo": "Test",
            "data": datetime.now(timezone.utc).isoformat()
        }
    ]
    errors = StateValidator.validate_requirements("em_andamento", arguments)
    assert not errors
    
    # Argumentos válidos para fechado
    arguments.append({
        "autor": "test_user",
        "tipo": "solucao",
        "conteudo": "Test",
        "data": datetime.now(timezone.utc).isoformat()
    })
    errors = StateValidator.validate_requirements("fechado", arguments)
    assert not errors
    
    # Sem argumentos suficientes
    errors = StateValidator.validate_requirements("em_andamento", [])
    assert errors
    assert any("mínimo" in error for error in errors)
    
    # Sem tipos requeridos
    arguments = [{
        "autor": "test_user",
        "tipo": "implementacao",
        "conteudo": "Test",
        "data": datetime.now(timezone.utc).isoformat()
    }]
    errors = StateValidator.validate_requirements("em_andamento", arguments)
    assert errors
    assert any("analise" in error for error in errors)

def test_validate_state_change(sample_embate):
    """Testa validação de mudança de estado"""
    # Mudança válida
    errors = StateValidator.validate_state_change(sample_embate, "em_andamento")
    assert not errors
    
    # Estado atual inválido
    invalid = sample_embate.copy()
    invalid['status'] = 'invalid'
    errors = StateValidator.validate_state_change(invalid, "em_andamento")
    assert errors
    assert any("atual" in error for error in errors)
    
    # Novo estado inválido
    errors = StateValidator.validate_state_change(sample_embate, "invalid")
    assert errors
    assert any("inválido" in error for error in errors)
    
    # Transição inválida
    errors = StateValidator.validate_state_change(sample_embate, "fechado")
    assert errors
    assert any("Transição" in error for error in errors)
    
    # Override de requisitos
    errors = StateValidator.validate_state_change(
        sample_embate,
        "fechado",
        allow_requirements_override=True
    )
    assert len(errors) == 1  # Apenas erro de transição

def test_get_state_history(sample_embate):
    """Testa obtenção de histórico de estados"""
    # Histórico inicial
    history = StateValidator.get_state_history(sample_embate)
    assert len(history) == 1
    assert history[0]['estado'] == 'aberto'
    
    # Adiciona mudança de estado
    sample_embate['argumentos'].append({
        "autor": "test_user",
        "tipo": "mudanca_estado",
        "conteudo": "em_andamento",
        "data": datetime.now(timezone.utc).isoformat()
    })
    
    history = StateValidator.get_state_history(sample_embate)
    assert len(history) == 2
    assert history[1]['estado'] == 'em_andamento'

def test_get_cycle_time(sample_embate):
    """Testa cálculo de tempo de ciclo"""
    # Embate em andamento
    cycle_time = StateValidator.get_cycle_time(sample_embate)
    assert cycle_time is not None
    assert cycle_time >= 0
    
    # Embate fechado
    sample_embate['status'] = 'fechado'
    sample_embate['argumentos'].append({
        "autor": "test_user",
        "tipo": "mudanca_estado",
        "conteudo": "fechado",
        "data": (
            datetime.now(timezone.utc) + timedelta(days=1)
        ).isoformat()
    })
    
    cycle_time = StateValidator.get_cycle_time(sample_embate)
    assert cycle_time is not None
    assert cycle_time >= 1  # Pelo menos 1 dia
    
    # Embate sem histórico
    invalid = sample_embate.copy()
    invalid.pop('data_inicio')
    cycle_time = StateValidator.get_cycle_time(invalid)
    assert cycle_time is None 