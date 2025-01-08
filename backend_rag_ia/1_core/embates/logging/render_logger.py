import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime

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
        
    def _format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Formata a mensagem no padrão JSON do Render"""
        log_data = {
            "message": message,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(log_data)
        
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Registra log de nível INFO"""
        self.logger.info(self._format_message(message, context))
        
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Registra log de nível ERROR"""
        self.logger.error(self._format_message(message, context))
        
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Registra log de nível WARNING"""
        self.logger.warning(self._format_message(message, context))
        
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Registra log de nível DEBUG"""
        self.logger.debug(self._format_message(message, context)) 