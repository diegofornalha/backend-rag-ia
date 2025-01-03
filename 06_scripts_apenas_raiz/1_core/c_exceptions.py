"""Exceções customizadas para o projeto."""

class BaseError(Exception):
    """Exceção base para o projeto."""

    def __init__(self, message: str = "") -> None:
        """Inicializa a exceção.

        Args:
            message: Mensagem de erro
        """
        self.message = message
        super().__init__(self.message)


class SupabaseError(BaseError):
    """Erro relacionado ao Supabase."""


class DatabaseError(BaseError):
    """Erro relacionado ao banco de dados."""


class EmbeddingError(BaseError):
    """Erro relacionado à geração de embeddings."""


class ValidationError(BaseError):
    """Erro de validação de dados."""


class ConfigError(BaseError):
    """Erro de configuração."""


class FileError(BaseError):
    """Erro relacionado a operações com arquivos."""
