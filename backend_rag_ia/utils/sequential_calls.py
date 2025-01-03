"""
Gerenciador de chamadas sequenciais.
Monitora e controla o número de chamadas sequenciais para evitar limites do Cursor.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import os
import shutil
import logging
from dataclasses import dataclass
from prometheus_client import Counter, Gauge

from ..cli.embates.manager import EmbateManager
from ..cli.embates.models import Embate, Argumento

@dataclass
class SequentialCallsConfig:
    """Configuração para o gerenciador de chamadas sequenciais."""
    LIMITE_AVISO: int = 20
    LIMITE_MAXIMO: int = 25
    TEMPO_RESET: int = 300  # 5 min
    STORAGE_PATH: str = '~/.rag_sequential_calls'
    NIVEIS_ALERTA: List[int] = [10, 15, 20, 23]
    BACKUP_ENABLED: bool = True
    MAX_BACKUP_FILES: int = 5
    VERSION: str = "2.0.0"

class ChamadasSequenciaisManager:
    """Gerencia e monitora chamadas sequenciais."""
    
    # Métricas Prometheus
    CHAMADAS_COUNTER = Counter('rag_chamadas_sequenciais_total', 'Total de chamadas sequenciais')
    CONTADOR_ATUAL = Gauge('rag_chamadas_sequenciais_atual', 'Contador atual de chamadas')
    ALERTAS_COUNTER = Counter('rag_chamadas_sequenciais_alertas', 'Total de alertas gerados')
    
    def __init__(self, config: Optional[SequentialCallsConfig] = None, storage_path: Optional[str] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            config: Configuração opcional
            storage_path: Caminho para persistir estado (opcional)
        """
        self.config = config or SequentialCallsConfig()
        self.contador = 0
        self.ultima_chamada = None
        self.storage_path = storage_path or os.path.expanduser(self.config.STORAGE_PATH)
        self.embate_manager = EmbateManager()
        
        # Configura logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Carrega estado anterior se existir
        self._carregar_estado()
        
        self.logger.info(f"ChamadasSequenciaisManager v{self.config.VERSION} iniciado")
        
    def registrar_chamada(self) -> Optional[Dict]:
        """
        Registra uma nova chamada e verifica limites.
        
        Returns:
            Dict com aviso se limite próximo, None caso contrário
        """
        agora = datetime.now()
        
        # Reseta contador se passou muito tempo
        if self.ultima_chamada and (agora - self.ultima_chamada).seconds > self.config.TEMPO_RESET:
            self.logger.info(f"Reset automático após {self.config.TEMPO_RESET}s de inatividade")
            self.contador = 0
            
        self.contador += 1
        self.ultima_chamada = agora
        
        # Atualiza métricas
        self.CHAMADAS_COUNTER.inc()
        self.CONTADOR_ATUAL.set(self.contador)
        
        self.logger.info(f"Chamada registrada: {self.contador}/{self.config.LIMITE_MAXIMO}")
        
        # Backup periódico
        if self.config.BACKUP_ENABLED and self.contador % 5 == 0:
            self._backup_estado()
        
        # Salva estado
        self._salvar_estado()
        
        # Verifica alertas
        return self._verificar_alertas()
        
    def resetar(self) -> None:
        """Reseta o contador de chamadas."""
        self.logger.info("Reset manual do contador")
        self.contador = 0
        self.ultima_chamada = None
        self._salvar_estado()
        self.CONTADOR_ATUAL.set(0)
        
    async def _verificar_alertas(self) -> Optional[Dict]:
        """Verifica se deve gerar alertas baseado nos níveis configurados."""
        for nivel in reversed(self.config.NIVEIS_ALERTA):
            if self.contador >= nivel:
                self.logger.warning(f"Alerta nível {nivel} atingido")
                self.ALERTAS_COUNTER.inc()
                return await self._criar_alerta(nivel)
        return None
        
    async def _criar_alerta(self, nivel: int) -> Dict:
        """Cria alerta para um nível específico."""
        # Determina severidade baseado no nível
        if nivel >= self.config.LIMITE_AVISO:
            severidade = "alta"
            tipo = "aviso"
        elif nivel >= 15:
            severidade = "média"
            tipo = "alerta"
        else:
            severidade = "baixa"
            tipo = "informativo"
            
        # Cria embate
        embate = Embate(
            titulo=f"{tipo.title()}: Nível {nivel} de Chamadas Sequenciais",
            tipo="sistema",
            contexto=f"""
            Você atingiu {nivel} chamadas sequenciais ({self.contador}/{self.config.LIMITE_MAXIMO}).
            Severidade: {severidade}
            """,
            status="aberto",
            data_inicio=datetime.now(),
            metadata={
                "is_sequential_call_warning": True,
                "nivel": nivel,
                "severidade": severidade
            }
        )
        
        # Adiciona sugestões baseadas no nível
        sugestoes = [
            "Faça uma pausa para revisar o progresso",
            "Salve o contexto atual",
            "Divida a tarefa em partes menores"
        ]
        
        if nivel >= self.config.LIMITE_AVISO:
            sugestoes.extend([
                "Considere finalizar a sessão atual",
                "Revise as últimas alterações"
            ])
            
        embate.argumentos.append(Argumento(
            autor="Sistema",
            tipo="sugestao",
            conteudo="\n".join(f"{i+1}. {s}" for i, s in enumerate(sugestoes)),
            data=datetime.now()
        ))
        
        # Salva embate
        result = await self.embate_manager.create_embate(embate)
        
        return {
            "tipo": tipo,
            "nivel": nivel,
            "severidade": severidade,
            "mensagem": f"Nível {nivel} de chamadas atingido",
            "contador": self.contador,
            "limite": self.config.LIMITE_MAXIMO,
            "embate_id": result.get("id"),
            "sugestoes": sugestoes
        }
        
    def _backup_estado(self) -> None:
        """Faz backup do estado atual."""
        if not self.config.BACKUP_ENABLED:
            return
            
        try:
            # Cria nome do backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.storage_path}.{timestamp}.bak"
            
            # Copia arquivo atual
            shutil.copy2(self.storage_path, backup_path)
            
            # Remove backups antigos se necessário
            self._limpar_backups()
            
            self.logger.info(f"Backup criado: {backup_path}")
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            
    def _limpar_backups(self) -> None:
        """Remove backups antigos mantendo apenas os mais recentes."""
        try:
            # Lista todos os backups
            backups = []
            for f in os.listdir(os.path.dirname(self.storage_path)):
                if f.startswith(os.path.basename(self.storage_path)) and f.endswith('.bak'):
                    backup_path = os.path.join(os.path.dirname(self.storage_path), f)
                    backups.append((os.path.getmtime(backup_path), backup_path))
                    
            # Remove mais antigos se exceder limite
            if len(backups) > self.config.MAX_BACKUP_FILES:
                for _, path in sorted(backups)[:-self.config.MAX_BACKUP_FILES]:
                    os.remove(path)
                    self.logger.info(f"Backup antigo removido: {path}")
        except Exception as e:
            self.logger.error(f"Erro ao limpar backups: {e}")
        
    def _salvar_estado(self) -> None:
        """Salva estado atual em arquivo."""
        estado = {
            "contador": self.contador,
            "ultima_chamada": self.ultima_chamada.isoformat() if self.ultima_chamada else None,
            "version": self.config.VERSION
        }
        
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(estado, f)
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado: {e}")
            
    def _carregar_estado(self) -> None:
        """Carrega estado anterior se existir."""
        if not os.path.exists(self.storage_path):
            return
            
        try:
            with open(self.storage_path) as f:
                estado = json.load(f)
                
            # Verifica versão para migração
            if estado.get("version", "1.0.0") != self.config.VERSION:
                self._migrar_estado(estado)
                
            self.contador = estado.get("contador", 0)
            ultima_chamada = estado.get("ultima_chamada")
            if ultima_chamada:
                self.ultima_chamada = datetime.fromisoformat(ultima_chamada)
                
            self.CONTADOR_ATUAL.set(self.contador)
            self.logger.info(f"Estado carregado: {self.contador} chamadas")
        except Exception as e:
            self.logger.error(f"Erro ao carregar estado: {e}")
            # Em caso de erro, usa valores default
            self.contador = 0
            self.ultima_chamada = None
            
    def _migrar_estado(self, estado_antigo: Dict) -> None:
        """Migra estado de versão antiga para atual."""
        self.logger.info(f"Migrando estado da versão {estado_antigo.get('version', '1.0.0')} para {self.config.VERSION}")
        # Por enquanto só faz backup do estado antigo
        self._backup_estado() 