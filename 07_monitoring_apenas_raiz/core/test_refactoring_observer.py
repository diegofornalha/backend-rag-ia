"""Testes para o sistema de observadores de refatoração."""

from datetime import datetime
import pytest

from refactoring_observer import (
    RefactoringEvent,
    ChatObserver,
    CodeObserver,
    RefactoringSubject
)

@pytest.fixture
def chat_observer():
    """Cria instância do ChatObserver para testes."""
    return ChatObserver()

@pytest.fixture
def code_observer():
    """Cria instância do CodeObserver para testes."""
    return CodeObserver()

@pytest.fixture
def subject():
    """Cria instância do RefactoringSubject para testes."""
    return RefactoringSubject()

def test_chat_observer_metrics():
    """Testa extração de métricas do chat."""
    observer = ChatObserver()
    
    event = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content="""
        Vamos remover o arquivo antigo e simplificar a função.
        Depois precisamos atualizar a documentação e consolidar as mudanças.
        """
    )
    
    result = observer.update(event)
    metrics = result["metrics"]
    
    assert metrics["removed"] == 1
    assert metrics["simplified"] == 1
    assert metrics["updated"] == 1
    assert metrics["consolidated"] == 1

def test_chat_observer_context():
    """Testa análise de contexto do chat."""
    observer = ChatObserver()
    
    event = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content="""
        O propósito mudou bastante e o escopo ficou mais complexo.
        Precisamos revisar se não estamos complicando demais.
        """
    )
    
    result = observer.update(event)
    context = result["context"]
    
    assert context["deviation"] is True
    assert context["scope_change"] is True
    assert context["complexity"] is True

def test_code_observer_metrics():
    """Testa métricas de código."""
    observer = CodeObserver()
    
    event = RefactoringEvent(
        timestamp=datetime.now(),
        type='code',
        content='diff',
        metrics={
            "removed": 10,
            "added": 5,
            "modified": 3,
            "moved": 2
        }
    )
    
    result = observer.update(event)
    metrics = result["metrics"]
    
    assert metrics["removed_lines"] == 10
    assert metrics["added_lines"] == 5
    assert metrics["modified_lines"] == 3
    assert metrics["moved_lines"] == 2

def test_observer_wrong_type():
    """Testa observador com tipo errado de evento."""
    chat_observer = ChatObserver()
    code_observer = CodeObserver()
    
    code_event = RefactoringEvent(
        timestamp=datetime.now(),
        type='code',
        content='diff'
    )
    
    chat_event = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content='mensagem'
    )
    
    assert chat_observer.update(code_event) == {}
    assert code_observer.update(chat_event) == {}

def test_subject_notification():
    """Testa notificação de observadores."""
    subject = RefactoringSubject()
    chat_observer = ChatObserver()
    code_observer = CodeObserver()
    
    subject.attach(chat_observer)
    subject.attach(code_observer)
    
    # Notifica evento de chat
    chat_event = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content='Vamos remover e simplificar o código'
    )
    subject.notify(chat_event)
    
    # Notifica evento de código
    code_event = RefactoringEvent(
        timestamp=datetime.now(),
        type='code',
        content='diff',
        metrics={"removed": 5, "added": 3}
    )
    subject.notify(code_event)
    
    analysis = subject.get_analysis()
    
    assert analysis["total_events"] == 2
    assert analysis["metrics"]["removed"] == 1
    assert analysis["metrics"]["simplified"] == 1
    assert analysis["metrics"]["removed_lines"] == 5
    assert analysis["metrics"]["added_lines"] == 3

def test_subject_detach():
    """Testa remoção de observador."""
    subject = RefactoringSubject()
    observer = ChatObserver()
    
    subject.attach(observer)
    assert observer in subject._observers
    
    subject.detach(observer)
    assert observer not in subject._observers

def test_subject_empty_history():
    """Testa análise com histórico vazio."""
    subject = RefactoringSubject()
    analysis = subject.get_analysis()
    
    assert "message" in analysis
    assert analysis["message"] == "Nenhum evento registrado"

def test_subject_deviations():
    """Testa detecção de desvios."""
    subject = RefactoringSubject()
    observer = ChatObserver()
    subject.attach(observer)
    
    # Evento com desvio de propósito
    event1 = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content='O propósito mudou completamente'
    )
    subject.notify(event1)
    
    # Evento com mudança de escopo
    event2 = RefactoringEvent(
        timestamp=datetime.now(),
        type='chat',
        content='O escopo está muito maior'
    )
    subject.notify(event2)
    
    analysis = subject.get_analysis()
    deviations = analysis["deviations"]
    
    assert deviations["purpose"] is True
    assert deviations["scope"] is True 