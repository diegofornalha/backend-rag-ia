import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EmbateValidationRule:
    rule_name: str
    validation_fn: callable
    error_message: str
    severity: str  # 'error', 'warning', 'info'


class EmbatesValidator:
    def __init__(self):
        self.validation_rules: list[EmbateValidationRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Configura regras padrão de validação"""
        self.add_rule(
            "limite_ferramentas",
            lambda x: x.get("tools_count", 0) <= 3,
            "Limite de 3 ferramentas excedido",
            "error",
        )

        self.add_rule(
            "aviso_preventivo",
            lambda x: self._check_preventive_warning(x),
            "Necessário aviso preventivo",
            "warning",
        )

        self.add_rule(
            "consistencia_datas",
            lambda x: self._validate_dates(x),
            "Inconsistência nas datas do embate",
            "error",
        )

        self.add_rule(
            "completude_dados",
            lambda x: self._check_required_fields(x),
            "Campos obrigatórios ausentes",
            "error",
        )

        self.add_rule(
            "validacao_metadata",
            lambda x: self._validate_metadata(x),
            "Metadata inválida ou incompleta",
            "warning",
        )

    def add_rule(
        self, name: str, validation_fn: callable, error_message: str, severity: str
    ) -> None:
        """Adiciona uma nova regra de validação"""
        rule = EmbateValidationRule(
            rule_name=name,
            validation_fn=validation_fn,
            error_message=error_message,
            severity=severity,
        )
        self.validation_rules.append(rule)

    def _check_preventive_warning(self, embate_data: dict) -> bool:
        """Verifica se os avisos preventivos estão configurados corretamente"""
        tools_count = embate_data.get("tools_count", 0)
        has_warning = embate_data.get("warnings", [])

        if tools_count == 2 and not has_warning:
            return False
        return True

    def _validate_dates(self, embate_data: dict) -> bool:
        """Valida consistência das datas"""
        data_inicio = embate_data.get("data_inicio")
        data_fim = embate_data.get("data_fim")

        if not data_inicio:
            return False

        try:
            inicio = datetime.fromisoformat(data_inicio)
            if data_fim:
                fim = datetime.fromisoformat(data_fim)
                if fim < inicio:
                    return False
        except ValueError:
            return False

        return True

    def _check_required_fields(self, embate_data: dict) -> bool:
        """Verifica campos obrigatórios"""
        required_fields = {"titulo", "tipo", "contexto", "status", "data_inicio", "argumentos"}

        return all(field in embate_data for field in required_fields)

    def _validate_metadata(self, embate_data: dict) -> bool:
        """Valida metadata do embate"""
        metadata = embate_data.get("metadata", {})
        required_metadata = {"impacto", "prioridade", "tags"}

        if not all(field in metadata for field in required_metadata):
            return False

        valid_impactos = {"baixo", "médio", "alto"}
        valid_prioridades = {"baixa", "média", "alta"}

        return (
            metadata["impacto"] in valid_impactos
            and metadata["prioridade"] in valid_prioridades
            and isinstance(metadata["tags"], list)
        )

    def validate_embate(self, embate_data: dict) -> list[dict[str, Any]]:
        """Executa todas as validações em um embate"""
        validation_results = []

        for rule in self.validation_rules:
            try:
                is_valid = rule.validation_fn(embate_data)
                if not is_valid:
                    validation_results.append(
                        {
                            "rule_name": rule.rule_name,
                            "error_message": rule.error_message,
                            "severity": rule.severity,
                        }
                    )
                    logger.warning(f"Validação falhou: {rule.rule_name} - {rule.error_message}")
            except Exception as e:
                logger.error(f"Erro na validação {rule.rule_name}: {str(e)}")
                validation_results.append(
                    {
                        "rule_name": rule.rule_name,
                        "error_message": f"Erro na validação: {str(e)}",
                        "severity": "error",
                    }
                )

        return validation_results
