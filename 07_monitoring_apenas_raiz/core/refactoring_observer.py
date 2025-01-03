"""Sistema de observadores para monitorar refatorações."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import re

@dataclass
class RefactoringEvent:
    """Evento de refatoração detectado."""
    timestamp: datetime
    type: str  # 'chat', 'code', 'commit'
    content: str
    metrics: Optional[Dict] = None
    context: Optional[Dict] = None

class RefactoringObserver(ABC):
    """Interface base para observadores de refatoração."""
    
    @abstractmethod
    def update(self, event: RefactoringEvent) -> None:
        """Processa um novo evento de refatoração."""
        pass

class ChatObserver(RefactoringObserver):
    """Observador que analisa mensagens do chat."""
    
    def __init__(self):
        self.patterns = {
            "removed": r"remov[er]\w*|delet\w+",
            "simplified": r"simplific\w+|refator\w+",
            "updated": r"atualiz\w+|modific\w+",
            "consolidated": r"consolid\w+|merg\w+|unific\w+"
        }
        self.purpose_patterns = {
            "deviation": r"diferente|mudou|alterou.*objetivo|prop[óo]sito",
            "scope_change": r"escopo|ampli\w+|reduz\w+",
            "complexity": r"complex[io]\w+|dif[íi]cil|complicad\w*|complic\w+"
        }
    
    def update(self, event: RefactoringEvent) -> Dict:
        """Analisa mensagem do chat."""
        if event.type != 'chat':
            return {}
            
        metrics = self._extract_metrics(event.content)
        context = self._analyze_context(event.content)
        
        return {
            "metrics": metrics,
            "context": context,
            "timestamp": event.timestamp
        }
    
    def _extract_metrics(self, content: str) -> Dict[str, int]:
        """Extrai métricas da mensagem."""
        metrics = {}
        content = content.lower()
        
        for metric, pattern in self.patterns.items():
            matches = re.findall(pattern, content)
            metrics[metric] = len(matches)
        
        return metrics
    
    def _analyze_context(self, content: str) -> Dict[str, bool]:
        """Analisa contexto da mensagem."""
        context = {}
        content = content.lower()
        
        for context_type, pattern in self.purpose_patterns.items():
            matches = re.findall(pattern, content)
            context[context_type] = len(matches) > 0
        
        return context

class CodeObserver(RefactoringObserver):
    """Observador que analisa mudanças no código."""
    
    def __init__(self):
        self.metrics = {
            "removed_lines": 0,
            "added_lines": 0,
            "modified_lines": 0,
            "moved_lines": 0
        }
    
    def update(self, event: RefactoringEvent) -> Dict:
        """Analisa mudanças no código."""
        if event.type != 'code':
            return {}
            
        # Analisa diff se disponível
        if event.metrics:
            self.metrics["removed_lines"] += event.metrics.get("removed", 0)
            self.metrics["added_lines"] += event.metrics.get("added", 0)
            self.metrics["modified_lines"] += event.metrics.get("modified", 0)
            self.metrics["moved_lines"] += event.metrics.get("moved", 0)
        
        return {
            "metrics": self.metrics.copy(),
            "timestamp": event.timestamp
        }

class RefactoringSubject:
    """Gerencia observadores e distribui eventos."""
    
    def __init__(self):
        self._observers: List[RefactoringObserver] = []
        self.history: List[Dict] = []
    
    def attach(self, observer: RefactoringObserver) -> None:
        """Adiciona um observador."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: RefactoringObserver) -> None:
        """Remove um observador."""
        self._observers.remove(observer)
    
    def notify(self, event: RefactoringEvent) -> None:
        """Notifica todos os observadores sobre um evento."""
        results = []
        for observer in self._observers:
            result = observer.update(event)
            if result:
                results.append({
                    "observer": observer.__class__.__name__,
                    "result": result
                })
        
        self.history.append({
            "event": event,
            "results": results,
            "timestamp": datetime.now()
        })
    
    def get_analysis(self) -> Dict:
        """Retorna análise agregada dos eventos."""
        if not self.history:
            return {"message": "Nenhum evento registrado"}
            
        # Agrega métricas
        metrics = {
            "removed": 0,
            "simplified": 0,
            "updated": 0,
            "consolidated": 0,
            "removed_lines": 0,
            "added_lines": 0,
            "modified_lines": 0
        }
        
        # Analisa desvios
        deviations = {
            "purpose": False,
            "scope": False,
            "complexity": False
        }
        
        for entry in self.history:
            for result in entry["results"]:
                if "metrics" in result["result"]:
                    for key, value in result["result"]["metrics"].items():
                        if key in metrics:
                            metrics[key] += value
                
                if "context" in result["result"]:
                    context = result["result"]["context"]
                    deviations["purpose"] |= context.get("deviation", False)
                    deviations["scope"] |= context.get("scope_change", False)
                    deviations["complexity"] |= context.get("complexity", False)
        
        return {
            "metrics": metrics,
            "deviations": deviations,
            "total_events": len(self.history),
            "period": {
                "start": self.history[0]["timestamp"],
                "end": self.history[-1]["timestamp"]
            }
        } 