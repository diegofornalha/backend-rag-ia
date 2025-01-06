from typing import Dict, Optional
import logging
import uuid
from datetime import datetime
from .embates_validator import EmbatesValidator
from .embates_counter import GlobalEmbatesCounter
from .embates_cache import EmbatesCache
from .embates_metrics import EmbatesMetrics, EmbateMetric

logger = logging.getLogger(__name__)


class EmbatesProtection:
    def __init__(self):
        self.validator = EmbatesValidator()
        self.protection_active = True

    def protect_embate(self, embate_data: Dict) -> Dict:
        """Aplica proteções e correções automáticas quando possível"""
        if not self.protection_active:
            return embate_data

        protected_data = embate_data.copy()

        # Proteção de datas
        if "data_inicio" not in protected_data:
            protected_data["data_inicio"] = datetime.now().isoformat()

        # Proteção de metadata
        if "metadata" not in protected_data:
            protected_data["metadata"] = {"impacto": "médio", "prioridade": "média", "tags": []}

        # Proteção de status
        if "status" not in protected_data:
            protected_data["status"] = "aberto"

        # Proteção de argumentos
        if "argumentos" not in protected_data:
            protected_data["argumentos"] = []

        # Proteção de tipo
        if "tipo" not in protected_data:
            protected_data["tipo"] = "tecnico"

        # Proteção de contexto
        if "contexto" not in protected_data:
            protected_data["contexto"] = "Contexto não especificado"

        return protected_data


class EmbatesProtectionManager:
    def __init__(self):
        self.protection = EmbatesProtection()
        self.validator = EmbatesValidator()
        self.counter = GlobalEmbatesCounter()
        self.cache = EmbatesCache()
        self.metrics = EmbatesMetrics()

    def process_embate(self, embate_data: Dict) -> Dict:
        """Processa um embate aplicando proteções e validações"""
        start_time = datetime.now()
        embate_id = embate_data.get("id", str(uuid.uuid4()))

        try:
            # Incrementa contador
            self.counter.increment(embate_id)

            # Verifica cache
            cached_result = self.cache.get_validation_result(embate_data)
            if cached_result:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics.record_operation(
                    EmbateMetric(
                        timestamp=datetime.now(),
                        embate_id=embate_id,
                        operation="cache_hit",
                        duration_ms=duration_ms,
                        success=True,
                        details={"source": "cache"},
                    )
                )
                return cached_result

            # Aplica proteções
            protected_data = self.protection.protect_embate(embate_data)

            # Valida resultado
            validation_results = self.validator.validate_embate(protected_data)

            if validation_results:
                errors = [r for r in validation_results if r["severity"] == "error"]
                warnings = [r for r in validation_results if r["severity"] == "warning"]

                # Log de avisos
                for warning in warnings:
                    logger.warning(f"Aviso na validação: {warning['error_message']}")

                # Se houver erros críticos, levanta exceção
                if errors:
                    error_messages = "\n".join([e["error_message"] for e in errors])
                    raise ValueError(f"Erros críticos encontrados:\n{error_messages}")

            # Armazena no cache
            self.cache.store_validation(embate_data, protected_data)

            # Registra métrica de sucesso
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_operation(
                EmbateMetric(
                    timestamp=datetime.now(),
                    embate_id=embate_id,
                    operation="process",
                    duration_ms=duration_ms,
                    success=True,
                    details={"validation_warnings": len(warnings) if "warnings" in locals() else 0},
                )
            )

            return protected_data

        except Exception as e:
            # Registra métrica de erro
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_operation(
                EmbateMetric(
                    timestamp=datetime.now(),
                    embate_id=embate_id,
                    operation="process",
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                    details={"error_message": str(e)},
                )
            )
            logger.error(f"Erro no processamento do embate: {str(e)}")
            raise

    def validate_only(self, embate_data: Dict) -> Dict[str, list]:
        """Apenas valida o embate sem aplicar proteções"""
        start_time = datetime.now()
        embate_id = embate_data.get("id", str(uuid.uuid4()))

        try:
            validation_results = self.validator.validate_embate(embate_data)

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_operation(
                EmbateMetric(
                    timestamp=datetime.now(),
                    embate_id=embate_id,
                    operation="validate_only",
                    duration_ms=duration_ms,
                    success=True,
                    details={"validation_count": len(validation_results)},
                )
            )

            return {
                "errors": [r for r in validation_results if r["severity"] == "error"],
                "warnings": [r for r in validation_results if r["severity"] == "warning"],
            }
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_operation(
                EmbateMetric(
                    timestamp=datetime.now(),
                    embate_id=embate_id,
                    operation="validate_only",
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                    details={"error_message": str(e)},
                )
            )
            raise

    def is_valid(self, embate_data: Dict) -> bool:
        """Verifica se um embate é válido (sem erros críticos)"""
        validation_results = self.validate_only(embate_data)
        return len(validation_results["errors"]) == 0

    def get_statistics(self) -> Dict:
        """Retorna estatísticas completas do sistema"""
        return {
            "counter": self.counter.get_statistics(),
            "cache": self.cache.get_statistics(),
            "metrics": self.metrics.get_statistics(),
        }
