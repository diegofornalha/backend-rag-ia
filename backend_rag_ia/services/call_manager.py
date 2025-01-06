"""
Gerenciador de chamadas sequenciais.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..cli.embates.models import Embate
from ..cli.embates.manager import EmbateManager


class ChamadaSequencial(BaseModel):
    """Modelo para uma chamada sequencial."""

    timestamp: datetime
    tipo: str
    contexto: Optional[str] = None


class ChamadasSequenciaisManager:
    """Gerencia chamadas sequenciais para evitar limites do Cursor."""

    def __init__(
        self,
        limite_retomada: int = 15,
        limite_maximo: int = 25,
        tempo_reset: int = 60,
        arquivo_estado: str = "chamadas_estado.json",
    ):
        """
        Inicializa o gerenciador.

        Args:
            limite_retomada: Número de chamadas para criar embate de retomada (default: 15)
            limite_maximo: Número máximo de chamadas permitidas
            tempo_reset: Tempo em minutos para resetar contador
            arquivo_estado: Arquivo para persistir estado
        """
        self.limite_retomada = limite_retomada
        self.limite_maximo = limite_maximo
        self.tempo_reset = tempo_reset
        self.arquivo_estado = Path(arquivo_estado)
        self.embate_manager = EmbateManager()

        self.chamadas: List[ChamadaSequencial] = []
        self._carregar_estado()

    async def registrar_chamada(self, tipo: str, contexto: Optional[str] = None) -> Dict:
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

        # Verifica limite máximo
        if len(self.chamadas) >= self.limite_maximo:
            return {
                "status": "error",
                "message": f"Limite de {self.limite_maximo} chamadas atingido",
            }

        # Registra chamada
        chamada = ChamadaSequencial(timestamp=agora, tipo=tipo, contexto=contexto)
        self.chamadas.append(chamada)

        # Persiste estado
        self._salvar_estado()

        # Verifica necessidade de retomada
        if len(self.chamadas) >= self.limite_retomada:
            await self._criar_embate_retomada()
            return {
                "status": "retomada",
                "message": f"Contamos {len(self.chamadas)} chamadas. Vamos retomar a execução.",
                "chamadas_restantes": self.limite_maximo - len(self.chamadas),
            }

        return {"status": "success"}

    async def _criar_embate_retomada(self) -> None:
        """Cria um embate simples para retomada."""
        embate = Embate(
            titulo=f"Retomada de Execução - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tipo="sistema",
            contexto=f"Atingido {len(self.chamadas)} chamadas. Criando ponto de retomada.",
            status="aberto",
            metadata={
                "chamadas_registradas": len(self.chamadas),
                "tipos_chamada": self._get_tipos_chamada(),
                "timestamp": datetime.now().isoformat(),
            },
        )

        await self.embate_manager.create_embate(embate)

    def _get_tipos_chamada(self) -> Dict[str, int]:
        """Retorna contagem de tipos de chamada."""
        tipos = {}
        for c in self.chamadas:
            tipos[c.tipo] = tipos.get(c.tipo, 0) + 1
        return tipos

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
                    contexto=c.get("contexto"),
                )
                for c in dados["chamadas"]
            ]
        except Exception:
            self.chamadas = []

    def _salvar_estado(self) -> None:
        """Salva estado no arquivo."""
        dados = {
            "chamadas": [
                {"timestamp": c.timestamp.isoformat(), "tipo": c.tipo, "contexto": c.contexto}
                for c in self.chamadas
            ]
        }
        self.arquivo_estado.write_text(json.dumps(dados, indent=2))
