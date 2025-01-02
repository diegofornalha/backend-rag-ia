"""
Gerenciador de chamadas sequenciais.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

class ChamadaSequencial(BaseModel):
    """Modelo para uma chamada sequencial."""
    timestamp: datetime
    tipo: str
    contexto: Optional[str] = None

class ChamadasSequenciaisManager:
    """Gerencia chamadas sequenciais para evitar limites do Cursor."""
    
    def __init__(self, 
                 limite_aviso: int = 20,
                 limite_maximo: int = 25,
                 tempo_reset: int = 60,
                 arquivo_estado: str = "chamadas_estado.json"):
        """
        Inicializa o gerenciador.
        
        Args:
            limite_aviso: Número de chamadas para gerar aviso
            limite_maximo: Número máximo de chamadas permitidas
            tempo_reset: Tempo em minutos para resetar contador
            arquivo_estado: Arquivo para persistir estado
        """
        self.limite_aviso = limite_aviso
        self.limite_maximo = limite_maximo
        self.tempo_reset = tempo_reset
        self.arquivo_estado = Path(arquivo_estado)
        
        self.chamadas: List[ChamadaSequencial] = []
        self._carregar_estado()
        
    def registrar_chamada(self, tipo: str, contexto: Optional[str] = None) -> Dict:
        """
        Registra uma nova chamada.
        
        Args:
            tipo: Tipo da chamada
            contexto: Contexto opcional
            
        Returns:
            Status do registro
        """
        agora = datetime.now()
        
        # Remove chamadas antigas
        self._limpar_chamadas_antigas(agora)
        
        # Verifica limite
        if len(self.chamadas) >= self.limite_maximo:
            return {
                "status": "error",
                "message": f"Limite de {self.limite_maximo} chamadas atingido"
            }
            
        # Registra chamada
        chamada = ChamadaSequencial(
            timestamp=agora,
            tipo=tipo,
            contexto=contexto
        )
        self.chamadas.append(chamada)
        
        # Persiste estado
        self._salvar_estado()
        
        # Verifica necessidade de aviso
        if len(self.chamadas) >= self.limite_aviso:
            return {
                "status": "warning",
                "message": f"Atingido {len(self.chamadas)} chamadas de {self.limite_maximo}",
                "sugestoes": self._gerar_sugestoes()
            }
            
        return {"status": "success"}
        
    def reset(self) -> None:
        """Reseta o contador de chamadas."""
        self.chamadas = []
        self._salvar_estado()
        
    def _limpar_chamadas_antigas(self, agora: datetime) -> None:
        """Remove chamadas mais antigas que o tempo de reset."""
        limite = agora - timedelta(minutes=self.tempo_reset)
        self.chamadas = [c for c in self.chamadas if c.timestamp > limite]
        
    def _carregar_estado(self) -> None:
        """Carrega estado do arquivo."""
        if not self.arquivo_estado.exists():
            return
            
        try:
            dados = json.loads(self.arquivo_estado.read_text())
            self.chamadas = [
                ChamadaSequencial(
                    timestamp=datetime.fromisoformat(c["timestamp"]),
                    tipo=c["tipo"],
                    contexto=c.get("contexto")
                )
                for c in dados["chamadas"]
            ]
        except Exception:
            self.chamadas = []
            
    def _salvar_estado(self) -> None:
        """Salva estado no arquivo."""
        dados = {
            "chamadas": [
                {
                    "timestamp": c.timestamp.isoformat(),
                    "tipo": c.tipo,
                    "contexto": c.contexto
                }
                for c in self.chamadas
            ]
        }
        self.arquivo_estado.write_text(json.dumps(dados, indent=2))
        
    def _gerar_sugestoes(self) -> List[str]:
        """Gera sugestões para reduzir chamadas."""
        sugestoes = [
            "Agrupe operações similares em uma única chamada",
            "Use cache para evitar chamadas repetidas",
            "Considere usar batch operations",
            f"Aguarde {self.tempo_reset} minutos para o contador resetar"
        ]
        
        # Analisa padrões nas chamadas
        tipos = {}
        for c in self.chamadas:
            tipos[c.tipo] = tipos.get(c.tipo, 0) + 1
            
        # Sugere otimizações baseadas nos tipos mais frequentes
        for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
            if count > 5:
                sugestoes.append(f"Otimize chamadas do tipo '{tipo}' ({count}x)")
                
        return sugestoes 