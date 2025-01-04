from typing import Dict, Optional
import logging
from datetime import datetime
from ..config.embates_config import EmbatesConfig
from ..monitoring.unified_monitor import UnifiedMonitor

logger = logging.getLogger(__name__)

class UnifiedProtection:
    def __init__(self, config: Optional[EmbatesConfig] = None):
        self.config = config or EmbatesConfig.get_default()
        self.monitor = UnifiedMonitor(self.config)
        self.protection_active = True
        
    def protect_embate(self, embate_data: Dict) -> Dict:
        """Aplica proteções e validações em um embate"""
        if not self.protection_active:
            return embate_data
            
        start_time = datetime.now()
        embate_id = embate_data.get('id', str(uuid.uuid4()))
        
        try:
            # Verifica limites de taxa
            if not self.monitor.check_rate_limit(embate_id):
                raise ValueError("Limite de taxa excedido")
            
            # Verifica cache
            cached_result = self.monitor.check_cache(embate_data)
            if cached_result:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.monitor.record_operation(
                    embate_id=embate_id,
                    operation='cache_hit',
                    duration_ms=duration_ms,
                    success=True,
                    details={'source': 'cache'}
                )
                return cached_result
            
            # Aplica proteções básicas
            protected_data = embate_data.copy()
            
            # Data início
            if 'data_inicio' not in protected_data:
                protected_data['data_inicio'] = datetime.now().isoformat()
            
            # Metadata
            if 'metadata' not in protected_data:
                protected_data['metadata'] = {
                    'impacto': 'médio',
                    'prioridade': 'média',
                    'tags': []
                }
            
            # Status
            if 'status' not in protected_data:
                protected_data['status'] = 'aberto'
            
            # Argumentos
            if 'argumentos' not in protected_data:
                protected_data['argumentos'] = []
            
            # Tipo
            if 'tipo' not in protected_data:
                protected_data['tipo'] = 'tecnico'
            
            # Contexto
            if 'contexto' not in protected_data:
                protected_data['contexto'] = 'Contexto não especificado'
            
            # Verifica avisos
            if self.monitor.should_warn(embate_id):
                logger.warning(f"Aviso: Embate {embate_id} próximo do limite de ferramentas")
            
            # Armazena no cache
            self.monitor.store_in_cache(embate_data, protected_data)
            
            # Registra operação
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.monitor.record_operation(
                embate_id=embate_id,
                operation='protect',
                duration_ms=duration_ms,
                success=True
            )
            
            return protected_data
            
        except Exception as e:
            # Registra erro
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.monitor.record_operation(
                embate_id=embate_id,
                operation='protect',
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                details={'error_message': str(e)}
            )
            raise
            
    def validate_embate(self, embate_data: Dict) -> Dict[str, list]:
        """Valida um embate sem aplicar proteções"""
        start_time = datetime.now()
        embate_id = embate_data.get('id', str(uuid.uuid4()))
        
        try:
            # Verifica campos obrigatórios
            required_fields = {
                'titulo', 'tipo', 'contexto', 'status',
                'data_inicio', 'argumentos'
            }
            
            missing_fields = required_fields - set(embate_data.keys())
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes: {missing_fields}")
            
            # Verifica metadata
            metadata = embate_data.get('metadata', {})
            required_metadata = {'impacto', 'prioridade', 'tags'}
            
            missing_metadata = required_metadata - set(metadata.keys())
            if missing_metadata:
                raise ValueError(f"Metadata obrigatória ausente: {missing_metadata}")
            
            # Verifica valores válidos
            valid_impactos = {'baixo', 'médio', 'alto'}
            valid_prioridades = {'baixa', 'média', 'alta'}
            
            if metadata['impacto'] not in valid_impactos:
                raise ValueError(f"Impacto inválido: {metadata['impacto']}")
                
            if metadata['prioridade'] not in valid_prioridades:
                raise ValueError(f"Prioridade inválida: {metadata['prioridade']}")
                
            if not isinstance(metadata['tags'], list):
                raise ValueError("Tags deve ser uma lista")
            
            # Registra sucesso
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.monitor.record_operation(
                embate_id=embate_id,
                operation='validate',
                duration_ms=duration_ms,
                success=True
            )
            
            return {'errors': [], 'warnings': []}
            
        except Exception as e:
            # Registra erro
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.monitor.record_operation(
                embate_id=embate_id,
                operation='validate',
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                details={'error_message': str(e)}
            )
            
            return {
                'errors': [{'message': str(e)}],
                'warnings': []
            }
            
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do sistema"""
        return self.monitor.get_statistics() 