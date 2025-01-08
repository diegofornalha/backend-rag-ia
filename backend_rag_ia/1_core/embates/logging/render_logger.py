import logging
import json
import traceback
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    """Níveis de log disponíveis"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Categorias de log para melhor organização"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    INTEGRATION = "integration"
    ERROR = "error"

class RenderLogger:
    """Logger integrado com o sistema nativo do Render"""
    
    def __init__(self, service_name: str = "embates"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self._configure_logger()
        
    def _configure_logger(self):
        """Configura o logger para formato compatível com Render"""
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"service": "%(name)s", "message": %(message)s}'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def _format_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> str:
        """Formata a mensagem no padrão JSON do Render"""
        log_data = {
            "message": message,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "category": category.value if category else None,
            "service": self.service_name
        }
        
        if extra_fields:
            log_data.update(extra_fields)
            
        return json.dumps(log_data)
        
    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        error: Optional[Exception] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        tags: Optional[List[str]] = None
    ):
        """Método base para logging com informações detalhadas"""
        extra_fields = {
            "tags": tags or []
        }
        
        if error:
            extra_fields.update({
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "stacktrace": traceback.format_exc()
            })
            
        if performance_metrics:
            extra_fields["performance"] = performance_metrics
            
        formatted_message = self._format_message(
            message,
            context,
            category,
            extra_fields
        )
        
        getattr(self.logger, level.value)(formatted_message)
        
    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log de nível DEBUG"""
        self._log(LogLevel.DEBUG, message, context, category, tags=tags)
        
    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log de nível INFO"""
        self._log(
            LogLevel.INFO,
            message,
            context,
            category,
            performance_metrics=performance_metrics,
            tags=tags
        )
        
    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log de nível WARNING"""
        self._log(LogLevel.WARNING, message, context, category, tags=tags)
        
    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        error: Optional[Exception] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log de nível ERROR"""
        self._log(
            LogLevel.ERROR,
            message,
            context,
            category or LogCategory.ERROR,
            error=error,
            tags=tags
        )
        
    def critical(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[LogCategory] = None,
        error: Optional[Exception] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log de nível CRITICAL"""
        self._log(
            LogLevel.CRITICAL,
            message,
            context,
            category or LogCategory.ERROR,
            error=error,
            tags=tags
        )
        
    def performance(
        self,
        message: str,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log específico de performance"""
        self._log(
            LogLevel.INFO,
            message,
            context,
            LogCategory.PERFORMANCE,
            performance_metrics=metrics,
            tags=tags
        )
        
    def security(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log específico de segurança"""
        self._log(
            LogLevel.WARNING,
            message,
            context,
            LogCategory.SECURITY,
            error=error,
            tags=tags
        )
        
    def business(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ):
        """Registra log específico de regras de negócio"""
        self._log(
            LogLevel.INFO,
            message,
            context,
            LogCategory.BUSINESS,
            tags=tags
        ) 