from typing import Dict, Optional
from datetime import datetime, timedelta

class ContainmentService:
    def __init__(self):
        self._rate_limits: Dict[str, dict] = {}
        self._cooldowns: Dict[str, datetime] = {}
        
    async def check_rate_limit(self, embate_id: str, limit_per_minute: int = 10) -> bool:
        """Verifica se o embate está dentro dos limites de taxa"""
        now = datetime.utcnow()
        
        if embate_id not in self._rate_limits:
            self._rate_limits[embate_id] = {
                "count": 0,
                "window_start": now
            }
            
        rate_data = self._rate_limits[embate_id]
        
        # Reset window if needed
        if now - rate_data["window_start"] > timedelta(minutes=1):
            rate_data["count"] = 0
            rate_data["window_start"] = now
            
        # Check limit
        if rate_data["count"] >= limit_per_minute:
            return False
            
        rate_data["count"] += 1
        return True
        
    async def set_cooldown(self, embate_id: str, minutes: int = 5):
        """Define um período de cooldown para um embate"""
        self._cooldowns[embate_id] = datetime.utcnow() + timedelta(minutes=minutes)
        
    async def check_cooldown(self, embate_id: str) -> Optional[timedelta]:
        """Verifica se um embate está em cooldown"""
        if embate_id not in self._cooldowns:
            return None
            
        now = datetime.utcnow()
        cooldown_end = self._cooldowns[embate_id]
        
        if now >= cooldown_end:
            del self._cooldowns[embate_id]
            return None
            
        return cooldown_end - now 