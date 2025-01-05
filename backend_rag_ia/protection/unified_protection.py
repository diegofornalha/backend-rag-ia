"""
Proteção unificada do sistema.
"""

import os
import uuid
from typing import Dict, Any, Optional

class UnifiedProtection:
    """Proteção unificada do sistema."""
    
    def __init__(self):
        """Inicializa a proteção."""
        self.protection_id = str(uuid.uuid4())
        self.enabled = True
        self.rules = {}
        
    def add_rule(self, rule_id: str, rule: Dict[str, Any]) -> None:
        """Adiciona uma regra de proteção."""
        self.rules[rule_id] = rule
        
    def remove_rule(self, rule_id: str) -> None:
        """Remove uma regra de proteção."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
    def check_protection(self, context: Dict[str, Any]) -> bool:
        """Verifica se o contexto está protegido."""
        if not self.enabled:
            return True
            
        for rule in self.rules.values():
            if not self._check_rule(rule, context):
                return False
                
        return True
        
    def _check_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica uma regra específica."""
        try:
            condition = rule.get("condition")
            if not condition:
                return True
                
            if isinstance(condition, str):
                return eval(condition, {"context": context})
                
            return condition(context)
            
        except Exception as e:
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status da proteção."""
        return {
            "id": self.protection_id,
            "enabled": self.enabled,
            "rules": len(self.rules)
        }
        
    def enable(self) -> None:
        """Habilita a proteção."""
        self.enabled = True
        
    def disable(self) -> None:
        """Desabilita a proteção."""
        self.enabled = False 