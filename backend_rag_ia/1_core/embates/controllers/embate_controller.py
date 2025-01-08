from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EmbateConfig:
    max_tokens: int
    temperature: float
    model_name: str
    tools_enabled: List[str]

class EmbateController:
    def __init__(self, config: EmbateConfig):
        self.config = config
        self._active_embates: Dict[str, dict] = {}
        
    async def create_embate(self, embate_id: str, context: dict) -> dict:
        """Cria um novo embate com configurações específicas"""
        if embate_id in self._active_embates:
            raise ValueError(f"Embate {embate_id} já existe")
            
        embate_data = {
            "id": embate_id,
            "status": "active",
            "context": context,
            "created_at": datetime.utcnow(),
            "config": self.config.__dict__
        }
        
        self._active_embates[embate_id] = embate_data
        return embate_data
        
    async def get_embate(self, embate_id: str) -> Optional[dict]:
        """Recupera dados de um embate específico"""
        return self._active_embates.get(embate_id)
        
    async def update_embate_status(self, embate_id: str, status: str) -> dict:
        """Atualiza o status de um embate"""
        if embate_id not in self._active_embates:
            raise ValueError(f"Embate {embate_id} não encontrado")
            
        self._active_embates[embate_id]["status"] = status
        return self._active_embates[embate_id] 