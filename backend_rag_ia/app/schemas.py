"""Módulo que define os schemas do sistema.

Este módulo contém as definições dos schemas Pydantic utilizados
para validação e serialização de dados na aplicação.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentBase(BaseModel):
    """Schema base para documentos.

    Attributes
    ----------
    titulo : str
        Título do documento.
    conteudo : str
        Conteúdo do documento.
    metadata : dict | None
        Metadados opcionais do documento.
    embedding : list[float] | None
        Embedding vetorial do documento.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    titulo: str
    conteudo: str
    metadata: dict | None = None
    embedding: list[float] | None = None


class DocumentCreate(DocumentBase):
    """Schema para criação de documentos.

    Herda todos os campos de DocumentBase.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    pass


class DocumentUpdate(BaseModel):
    """Schema para atualização de documentos.

    Attributes
    ----------
    titulo : Optional[str]
        Novo título do documento.
    conteudo : Optional[str]
        Novo conteúdo do documento.
    metadata : Optional[dict]
        Novos metadados do documento.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    titulo: Optional[str] = None
    conteudo: Optional[str] = None
    metadata: Optional[dict] = None


class Document(DocumentBase):
    """Schema completo de documento.

    Attributes
    ----------
    id : str
        Identificador único do documento.
    created_at : datetime | None
        Data de criação do documento.
    updated_at : datetime | None
        Data da última atualização.
    embedding_updated_at : datetime | None
        Data da última atualização do embedding.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    embedding_updated_at: datetime | None = None

    class Config:
        """Configuração do modelo."""
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        orm_mode = True


class EmbeddingCreate(BaseModel):
    """Schema para geração de embeddings.

    Attributes
    ----------
    text : str
        Texto para gerar o embedding.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    text: str


class Embedding(BaseModel):
    """Schema completo de embedding.

    Attributes
    ----------
    id : str
        Identificador único do embedding.
    document_id : str
        Identificador do documento associado.
    vector : list[float]
        Vetor do embedding.
    created_at : datetime | None
        Data de criação.
    updated_at : datetime | None
        Data da última atualização.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    id: str
    document_id: str
    vector: list[float]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        """Configuração do modelo."""
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        orm_mode = True


class Statistics(BaseModel):
    """Schema para estatísticas do sistema.

    Attributes
    ----------
    id : str
        Identificador único da estatística.
    total_documents : int
        Total de documentos no sistema.
    documents_with_embedding : int
        Total de documentos com embedding.
    average_document_length : float
        Comprimento médio dos documentos.
    created_at : datetime | None
        Data de criação da estatística.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    id: str
    total_documents: int
    documents_with_embedding: int
    average_document_length: float
    created_at: datetime | None = None

    class Config:
        """Configuração do modelo."""
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        orm_mode = True


class LogEntry(BaseModel):
    """Schema para entradas de log.

    Attributes
    ----------
    id : str
        Identificador único do log.
    level : str
        Nível do log.
    message : str
        Mensagem do log.
    metadata : dict | None
        Metadados opcionais do log.
    created_at : datetime | None
        Data de criação do log.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    id: str
    level: str
    message: str
    metadata: dict | None = None
    created_at: datetime | None = None


class BatchOperation(BaseModel):
    """Schema para operações em lote.

    Attributes
    ----------
    id : str
        Identificador único da operação.
    operation_type : str
        Tipo da operação.
    status : str
        Status atual da operação.
    total_items : int
        Total de itens a processar.
    processed_items : int
        Total de itens processados.
    errors : list[str] | None
        Lista de erros ocorridos.
    created_at : datetime | None
        Data de criação da operação.
    updated_at : datetime | None
        Data da última atualização.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    id: str
    operation_type: str
    status: str
    total_items: int
    processed_items: int
    errors: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        """Configuração do modelo."""
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        orm_mode = True


class HealthCheck(BaseModel):
    """Schema para verificação de saúde do sistema.

    Attributes
    ----------
    status : str
        Status atual do sistema.
    version : str
        Versão do sistema.
    timestamp : datetime | None
        Data e hora da verificação.

    """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    status: str
    version: str
    timestamp: datetime | None = None
