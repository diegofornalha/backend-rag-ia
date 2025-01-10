import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class TypeValidationError(Exception):
    """Erro de validação de tipo"""

    pass


class TypeValidator:
    """Middleware para validação de tipos"""

    @staticmethod
    def validate_type(value: Any, expected_type: type) -> bool:
        """
        Valida se um valor corresponde ao tipo esperado

        Args:
            value: Valor a ser validado
            expected_type: Tipo esperado

        Returns:
            True se o tipo corresponde, False caso contrário
        """
        # Trata tipos genéricos (List, Dict, etc)
        if hasattr(expected_type, "__origin__"):
            origin = expected_type.__origin__
            args = expected_type.__args__

            # Lista
            if origin == list:
                if not isinstance(value, list):
                    return False
                # Valida tipo dos elementos
                element_type = args[0]
                return all(TypeValidator.validate_type(item, element_type) for item in value)

            # Dicionário
            if origin == dict:
                if not isinstance(value, dict):
                    return False
                # Valida tipos das chaves e valores
                key_type, value_type = args
                return all(
                    TypeValidator.validate_type(k, key_type)
                    and TypeValidator.validate_type(v, value_type)
                    for k, v in value.items()
                )

            # Union/Optional
            if origin == Union:
                return any(TypeValidator.validate_type(value, t) for t in args)

        # Tipos básicos
        return isinstance(value, expected_type)

    @staticmethod
    def validate_args(func: Callable) -> Callable:
        """
        Decorator para validar argumentos de função

        Args:
            func: Função a ser decorada

        Returns:
            Função decorada com validação de tipos
        """
        # Obtém assinatura da função
        sig = inspect.signature(func)
        parameters = sig.parameters

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Combina args e kwargs
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Valida cada argumento
            for name, value in bound_args.arguments.items():
                param = parameters[name]

                # Pula se não tem anotação de tipo
                if param.annotation == inspect.Parameter.empty:
                    continue

                # Valida tipo
                if not TypeValidator.validate_type(value, param.annotation):
                    raise TypeValidationError(
                        f"Argumento '{name}' deve ser do tipo {param.annotation}, "
                        f"mas recebeu {type(value)}"
                    )

            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def validate_return(func: Callable) -> Callable:
        """
        Decorator para validar retorno de função

        Args:
            func: Função a ser decorada

        Returns:
            Função decorada com validação de tipo de retorno
        """
        # Obtém tipo de retorno
        sig = inspect.signature(func)
        return_type = sig.return_annotation

        # Pula se não tem anotação de retorno
        if return_type == inspect.Parameter.empty:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Valida tipo do retorno
            if not TypeValidator.validate_type(result, return_type):
                raise TypeValidationError(
                    f"Retorno deve ser do tipo {return_type}, " f"mas recebeu {type(result)}"
                )

            return result

        return wrapper

    @staticmethod
    def validate(func: Callable) -> Callable:
        """
        Decorator que combina validação de argumentos e retorno

        Args:
            func: Função a ser decorada

        Returns:
            Função decorada com validação completa de tipos
        """
        return TypeValidator.validate_return(TypeValidator.validate_args(func))


# Exemplo de uso:
"""
from typing import List, Dict, Optional

@TypeValidator.validate
def process_data(items: List[Dict[str, Any]], config: Optional[Dict[str, str]] = None) -> List[str]:
    # Função com validação de tipos
    pass
"""
