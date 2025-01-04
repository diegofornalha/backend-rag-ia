"""Exceções customizadas para tratamento de erros específicos da aplicação."""


class BaseError(Exception):
    """Exceção base para todas as exceções customizadas.

    Esta classe serve como base para todas as outras exceções
    específicas da aplicação.

    """

    pass


class SupabaseError(BaseError):
    """Erro de conexão ou operação com Supabase.

    Esta exceção é lançada quando ocorrem problemas na
    comunicação ou operação com o Supabase.

    """

    pass


class DatabaseError(BaseError):
    """Erro de operação no banco de dados.

    Esta exceção é lançada quando ocorrem problemas em
    operações no banco de dados.

    """

    pass


class EmbeddingError(BaseError):
    """Erro ao gerar ou processar embeddings.

    Esta exceção é lançada quando ocorrem problemas na
    geração ou processamento de embeddings.

    """

    pass


class LLMError(BaseError):
    """Erro ao processar com modelo de linguagem.

    Esta exceção é lançada quando ocorrem problemas no
    processamento com modelos de linguagem.

    """

    pass


class ValidationError(BaseError):
    """Erro de validação de dados.

    Esta exceção é lançada quando ocorrem problemas na
    validação de dados de entrada ou saída.

    """

    pass
