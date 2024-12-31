"""Exceções customizadas do projeto."""

class ValidationError(Exception):
    """Exceção para erros de validação."""
    pass

class DatabaseError(Exception):
    """Exceção para erros de banco de dados."""
    pass

class EmbeddingError(Exception):
    """Exceção para erros na geração de embeddings."""
    pass

class SupabaseError(Exception):
    """Exceção para erros relacionados ao Supabase."""
    pass 