from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..interfaces.embate_interfaces import EmbateContext, EmbateResult

@dataclass
class DefaultEmbateContext(EmbateContext):
    """Implementação padrão do contexto de embates"""
    
    _embate_id: str
    _created_at: datetime
    _metadata: Dict[str, Any]
    _parameters: Dict[str, Any]
    
    @property
    def embate_id(self) -> str:
        return self._embate_id
        
    @property
    def created_at(self) -> datetime:
        return self._created_at
        
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata
        
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters
        
    @classmethod
    def create(
        cls,
        embate_id: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'DefaultEmbateContext':
        """Cria uma nova instância de contexto"""
        return cls(
            _embate_id=embate_id,
            _created_at=datetime.utcnow(),
            _metadata=metadata or {},
            _parameters=parameters
        )

@dataclass
class DefaultEmbateResult(EmbateResult):
    """Implementação padrão do resultado de embates"""
    
    _embate_id: str
    _success: bool
    _data: Dict[str, Any]
    _metrics: Dict[str, float]
    _errors: List[Dict[str, Any]]
    
    @property
    def embate_id(self) -> str:
        return self._embate_id
        
    @property
    def success(self) -> bool:
        return self._success
        
    @property
    def data(self) -> Dict[str, Any]:
        return self._data
        
    @property
    def metrics(self) -> Dict[str, float]:
        return self._metrics
        
    @property
    def errors(self) -> List[Dict[str, Any]]:
        return self._errors
        
    @classmethod
    def success_result(
        cls,
        embate_id: str,
        data: Dict[str, Any],
        metrics: Optional[Dict[str, float]] = None
    ) -> 'DefaultEmbateResult':
        """Cria um resultado de sucesso"""
        return cls(
            _embate_id=embate_id,
            _success=True,
            _data=data,
            _metrics=metrics or {},
            _errors=[]
        )
        
    @classmethod
    def error_result(
        cls,
        embate_id: str,
        error: Exception,
        metrics: Optional[Dict[str, float]] = None
    ) -> 'DefaultEmbateResult':
        """Cria um resultado de erro"""
        return cls(
            _embate_id=embate_id,
            _success=False,
            _data={},
            _metrics=metrics or {},
            _errors=[{
                "type": type(error).__name__,
                "message": str(error)
            }]
        )
        
    def add_error(self, error: Exception):
        """Adiciona um erro ao resultado"""
        self._errors.append({
            "type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        })
        self._success = False
        
    def add_metric(self, name: str, value: float):
        """Adiciona uma métrica ao resultado"""
        self._metrics[name] = value
        
    def update_data(self, data: Dict[str, Any]):
        """Atualiza dados do resultado"""
        self._data.update(data) 