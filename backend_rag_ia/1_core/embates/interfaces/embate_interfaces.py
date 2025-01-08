from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class EmbateContext(Protocol):
    """Interface para contexto de embates"""
    
    @property
    def embate_id(self) -> str:
        """ID único do embate"""
        ...
        
    @property
    def created_at(self) -> datetime:
        """Data de criação"""
        ...
        
    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadados do embate"""
        ...
        
    @property
    def parameters(self) -> Dict[str, Any]:
        """Parâmetros do embate"""
        ...

@runtime_checkable
class EmbateResult(Protocol):
    """Interface para resultado de embates"""
    
    @property
    def embate_id(self) -> str:
        """ID do embate"""
        ...
        
    @property
    def success(self) -> bool:
        """Se o embate foi bem-sucedido"""
        ...
        
    @property
    def data(self) -> Dict[str, Any]:
        """Dados do resultado"""
        ...
        
    @property
    def metrics(self) -> Dict[str, float]:
        """Métricas do processamento"""
        ...
        
    @property
    def errors(self) -> List[Dict[str, Any]]:
        """Lista de erros, se houver"""
        ...

class IEmbateCache(ABC):
    """Interface para cache de embates"""
    
    @abstractmethod
    async def get_result(
        self,
        context_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Recupera resultado do cache"""
        pass
        
    @abstractmethod
    async def store_result(
        self,
        context_hash: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Armazena resultado no cache"""
        pass
        
    @abstractmethod
    async def invalidate_result(self, context_hash: str):
        """Invalida resultado no cache"""
        pass

class IEmbateEvents(ABC):
    """Interface para eventos de embates"""
    
    @abstractmethod
    async def on_embate_started(
        self,
        embate_id: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica início de embate"""
        pass
        
    @abstractmethod
    async def on_embate_completed(
        self,
        embate_id: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica conclusão de embate"""
        pass
        
    @abstractmethod
    async def on_embate_failed(
        self,
        embate_id: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica falha em embate"""
        pass

class IEmbateStrategy(ABC):
    """Interface para estratégias de embate"""
    
    @abstractmethod
    async def process(
        self,
        context: EmbateContext,
        cache: IEmbateCache,
        events: IEmbateEvents
    ) -> EmbateResult:
        """Processa um embate"""
        pass
        
    @abstractmethod
    async def validate(self, context: EmbateContext) -> bool:
        """Valida contexto do embate"""
        pass
        
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Nome da estratégia"""
        pass

class IEmbateProcessor(ABC):
    """Interface para processador de embates"""
    
    @abstractmethod
    async def process_embate(
        self,
        context: EmbateContext,
        strategy: Optional[str] = None
    ) -> EmbateResult:
        """Processa um embate"""
        pass
        
    @abstractmethod
    async def register_strategy(
        self,
        strategy: IEmbateStrategy
    ):
        """Registra uma nova estratégia"""
        pass
        
    @abstractmethod
    def get_available_strategies(self) -> List[str]:
        """Retorna estratégias disponíveis"""
        pass

class IEmbateMetrics(ABC):
    """Interface para métricas de embates"""
    
    @abstractmethod
    async def record_processing_time(
        self,
        embate_id: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra tempo de processamento"""
        pass
        
    @abstractmethod
    async def record_tokens_used(
        self,
        embate_id: str,
        tokens: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra tokens utilizados"""
        pass
        
    @abstractmethod
    async def record_success(
        self,
        embate_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra sucesso"""
        pass
        
    @abstractmethod
    async def record_failure(
        self,
        embate_id: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra falha"""
        pass

class IEmbateLogger(ABC):
    """Interface para logging de embates"""
    
    @abstractmethod
    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra log de nível INFO"""
        pass
        
    @abstractmethod
    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra log de nível ERROR"""
        pass
        
    @abstractmethod
    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra log de nível WARNING"""
        pass
        
    @abstractmethod
    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra log de nível DEBUG"""
        pass 