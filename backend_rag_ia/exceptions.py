"""Exceções customizadas."""

class BaseError(Exception):
    """Exceção base."""
    pass

class SupabaseError(BaseError):
    """Erro de conexão com Supabase."""
    pass

class DatabaseError(BaseError):
    """Erro de operação no banco."""
    pass

class EmbeddingError(BaseError):
    """Erro ao gerar embedding."""
    pass

class LLMError(BaseError):
    """Erro ao processar com LLM."""
    pass

class ValidationError(BaseError):
    """Erro de validação de dados."""
    pass 