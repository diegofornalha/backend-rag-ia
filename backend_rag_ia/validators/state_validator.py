import logging
from datetime import datetime
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class StateValidationError(Exception):
    """Erro de validação de estado"""

    pass


class StateValidator:
    """Validador de transições de estado"""

    # Estados válidos
    VALID_STATES = {"aberto", "em_andamento", "bloqueado", "fechado"}

    # Transições válidas
    VALID_TRANSITIONS = {
        "aberto": {"em_andamento", "bloqueado", "fechado"},
        "em_andamento": {"bloqueado", "fechado"},
        "bloqueado": {"em_andamento", "fechado"},
        "fechado": set(),  # Estado final
    }

    # Requisitos para transição
    TRANSITION_REQUIREMENTS = {
        "em_andamento": {"min_arguments": 1, "required_types": {"analise"}},
        "fechado": {"min_arguments": 2, "required_types": {"analise", "solucao"}},
    }

    @staticmethod
    def validate_state(state: str) -> bool:
        """
        Valida se um estado é válido

        Args:
            state: Estado a ser validado

        Returns:
            True se o estado é válido, False caso contrário
        """
        return state in StateValidator.VALID_STATES

    @staticmethod
    def validate_transition(current_state: str, new_state: str) -> bool:
        """
        Valida se uma transição de estado é válida

        Args:
            current_state: Estado atual
            new_state: Novo estado

        Returns:
            True se a transição é válida, False caso contrário
        """
        # Valida estados
        if not StateValidator.validate_state(current_state):
            return False
        if not StateValidator.validate_state(new_state):
            return False

        # Valida transição
        return new_state in StateValidator.VALID_TRANSITIONS[current_state]

    @staticmethod
    def get_valid_transitions(current_state: str) -> set[str]:
        """
        Retorna os estados válidos para transição

        Args:
            current_state: Estado atual

        Returns:
            Conjunto de estados válidos para transição
        """
        if not StateValidator.validate_state(current_state):
            return set()

        return StateValidator.VALID_TRANSITIONS[current_state]

    @staticmethod
    def validate_requirements(new_state: str, arguments: list[dict]) -> list[str]:
        """
        Valida requisitos para transição de estado

        Args:
            new_state: Novo estado
            arguments: Lista de argumentos do embate

        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []

        # Verifica se tem requisitos
        if new_state not in StateValidator.TRANSITION_REQUIREMENTS:
            return errors

        requirements = StateValidator.TRANSITION_REQUIREMENTS[new_state]

        # Valida quantidade mínima de argumentos
        if len(arguments) < requirements["min_arguments"]:
            errors.append(
                f"Estado '{new_state}' requer no mínimo "
                f"{requirements['min_arguments']} argumento(s)"
            )

        # Valida tipos de argumentos
        argument_types = {arg["tipo"] for arg in arguments}
        missing_types = requirements["required_types"] - argument_types
        if missing_types:
            errors.append(
                f"Estado '{new_state}' requer argumentos do(s) tipo(s): "
                f"{', '.join(missing_types)}"
            )

        return errors

    @staticmethod
    def validate_state_change(
        embate: dict, new_state: str, allow_requirements_override: bool = False
    ) -> list[str]:
        """
        Valida uma mudança de estado completa

        Args:
            embate: Dicionário com dados do embate
            new_state: Novo estado
            allow_requirements_override: Se True, ignora validação de requisitos

        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []

        # Valida estado atual
        current_state = embate.get("status")
        if not current_state:
            errors.append("Embate não possui estado atual")
            return errors

        if not StateValidator.validate_state(current_state):
            errors.append(f"Estado atual '{current_state}' é inválido")
            return errors

        # Valida novo estado
        if not StateValidator.validate_state(new_state):
            errors.append(f"Novo estado '{new_state}' é inválido")
            return errors

        # Valida transição
        if not StateValidator.validate_transition(current_state, new_state):
            valid_transitions = StateValidator.get_valid_transitions(current_state)
            errors.append(
                f"Transição de '{current_state}' para '{new_state}' é inválida. "
                f"Transições válidas: {', '.join(valid_transitions)}"
            )

        # Valida requisitos
        if not allow_requirements_override:
            arguments = embate.get("argumentos", [])
            requirement_errors = StateValidator.validate_requirements(new_state, arguments)
            errors.extend(requirement_errors)

        return errors

    @staticmethod
    def get_state_history(embate: dict) -> list[dict]:
        """
        Retorna histórico de mudanças de estado

        Args:
            embate: Dicionário com dados do embate

        Returns:
            Lista de mudanças de estado
        """
        history = []

        # Estado inicial
        if "data_inicio" in embate:
            history.append(
                {
                    "estado": "aberto",
                    "data": embate["data_inicio"],
                    "autor": embate.get("autor", "sistema"),
                }
            )

        # Mudanças de estado nos argumentos
        for arg in embate.get("argumentos", []):
            if arg["tipo"] == "mudanca_estado":
                history.append(
                    {"estado": arg["conteudo"], "data": arg["data"], "autor": arg["autor"]}
                )

        return history

    @staticmethod
    def get_cycle_time(embate: dict) -> float | None:
        """
        Calcula o tempo de ciclo do embate (em dias)

        Args:
            embate: Dicionário com dados do embate

        Returns:
            Tempo de ciclo em dias ou None se não puder calcular
        """
        try:
            # Obtém histórico
            history = StateValidator.get_state_history(embate)
            if not history:
                return None

            # Encontra primeira e última data
            start_date = datetime.fromisoformat(history[0]["data"].replace("Z", "+00:00"))

            # Se ainda não está fechado, usa data atual
            current_state = embate.get("status")
            if current_state == "fechado":
                last_change = history[-1]
                end_date = datetime.fromisoformat(last_change["data"].replace("Z", "+00:00"))
            else:
                end_date = datetime.now()

            # Calcula diferença em dias
            diff = end_date - start_date
            return diff.total_seconds() / (24 * 60 * 60)  # Converte para dias

        except Exception as e:
            logger.error(f"Erro ao calcular tempo de ciclo: {str(e)}")
            return None
