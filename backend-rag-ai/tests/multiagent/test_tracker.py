"""
Testes para o sistema de tracking do multiagente.
"""

import pytest
from backend_rag_ia.services.multiagent.core.tracker import EventTracker

def test_event_tracking():
    """Testa o registro básico de eventos."""
    tracker = EventTracker()
    
    # Registra alguns eventos
    tracker.track_event("test_event", {"value": 1})
    tracker.track_event("test_event", {"value": 2})
    tracker.track_event("other_event")
    
    # Verifica métricas
    metrics = tracker.get_metrics()
    assert metrics["total_events"] == 3
    assert metrics["events_by_type"]["test_event"] == 2
    assert metrics["events_by_type"]["other_event"] == 1
    assert metrics["elapsed_time"] > 0

def test_disabled_tracking():
    """Testa o tracking desabilitado."""
    tracker = EventTracker()
    tracker.config.tracking_enabled = False
    
    # Tenta registrar eventos
    tracker.track_event("test_event")
    tracker.track_event("other_event")
    
    # Verifica que nada foi registrado
    metrics = tracker.get_metrics()
    assert metrics["total_events"] == 0
    assert metrics["events_by_type"] == {}

def test_clear_events():
    """Testa a limpeza de eventos."""
    tracker = EventTracker()
    
    # Registra eventos
    tracker.track_event("test_event")
    tracker.track_event("other_event")
    
    # Limpa eventos
    tracker.clear()
    
    # Verifica que foram limpos
    metrics = tracker.get_metrics()
    assert metrics["total_events"] == 0
    assert metrics["events_by_type"] == {} 