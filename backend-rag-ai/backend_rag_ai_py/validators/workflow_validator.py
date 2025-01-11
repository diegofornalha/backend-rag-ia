import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkflowValidator:
    # Sequências válidas de tipos de argumentos por tipo de embate
    VALID_SEQUENCES = {
        "feature": ["analise", "solucao", "implementacao", "validacao"],
        "bug": ["problema", "analise", "solucao", "validacao"],
        "processo": ["analise", "solucao", "implementacao", "validacao"],
        "tech_debt": ["analise", "solucao", "implementacao", "validacao"],
    }

    # Estados válidos e suas transições permitidas
    VALID_TRANSITIONS = {
        "aberto": ["em_andamento", "fechado"],
        "em_andamento": ["fechado", "bloqueado"],
        "bloqueado": ["em_andamento", "fechado"],
        "fechado": [],
    }

    @staticmethod
    def validate_sequence(embate: dict) -> list[str]:
        """Valida sequência de argumentos"""
        errors = []

        # Verifica sequência de argumentos
        argumentos = embate.get("argumentos", [])
        tipo_embate = embate.get("tipo")

        if tipo_embate in WorkflowValidator.VALID_SEQUENCES:
            sequencia = WorkflowValidator.VALID_SEQUENCES[tipo_embate]
            tipos_encontrados = [arg["tipo"] for arg in argumentos]

            # Verifica ordem
            for i, tipo in enumerate(tipos_encontrados):
                if i >= len(sequencia):
                    break
                if tipo != sequencia[i]:
                    errors.append(
                        f"Sequência incorreta: esperado {sequencia[i]}, "
                        f"encontrado {tipo} na posição {i+1}"
                    )
        else:
            errors.append(f"Tipo de embate inválido: {tipo_embate}")

        return errors

    @staticmethod
    def validate_state_transition(old_state: str, new_state: str) -> str | None:
        """Valida transição de estado"""
        if old_state not in WorkflowValidator.VALID_TRANSITIONS:
            return f"Estado atual inválido: {old_state}"

        if new_state not in WorkflowValidator.VALID_TRANSITIONS[old_state]:
            return (
                f"Transição inválida de {old_state} para {new_state}. "
                f"Transições válidas: {WorkflowValidator.VALID_TRANSITIONS[old_state]}"
            )

        return None

    @staticmethod
    def validate_metadata(embate: dict) -> list[str]:
        """Valida metadata do embate"""
        errors = []
        metadata = embate.get("metadata", {})

        # Campos obrigatórios
        required_fields = {"impacto", "prioridade", "tags"}
        missing = required_fields - set(metadata.keys())
        if missing:
            errors.append(f"Campos obrigatórios ausentes em metadata: {missing}")

        # Valores válidos
        valid_impactos = {"baixo", "médio", "alto"}
        if metadata.get("impacto") not in valid_impactos:
            errors.append(
                f'Impacto inválido: {metadata.get("impacto")}. '
                f'Valores válidos: {valid_impactos}'
            )

        valid_prioridades = {"baixa", "média", "alta"}
        if metadata.get("prioridade") not in valid_prioridades:
            errors.append(
                f'Prioridade inválida: {metadata.get("prioridade")}. '
                f'Valores válidos: {valid_prioridades}'
            )

        if not isinstance(metadata.get("tags", []), list):
            errors.append("Tags deve ser uma lista")

        return errors

    @staticmethod
    def validate_dates(embate: dict) -> list[str]:
        """Valida datas do embate"""
        errors = []

        try:
            # Data início
            data_inicio = datetime.fromisoformat(embate.get("data_inicio", ""))

            # Datas dos argumentos
            for i, arg in enumerate(embate.get("argumentos", [])):
                data_arg = datetime.fromisoformat(arg.get("data", ""))
                if data_arg < data_inicio:
                    errors.append(
                        f"Data do argumento {i+1} ({data_arg}) é anterior "
                        f"à data de início do embate ({data_inicio})"
                    )
        except ValueError as e:
            errors.append(f"Erro no formato das datas: {str(e)}")

        return errors

    @staticmethod
    def validate_embate(embate: dict) -> dict[str, list[str]]:
        """Valida embate completo"""
        return {
            "sequence": WorkflowValidator.validate_sequence(embate),
            "metadata": WorkflowValidator.validate_metadata(embate),
            "dates": WorkflowValidator.validate_dates(embate),
        }
