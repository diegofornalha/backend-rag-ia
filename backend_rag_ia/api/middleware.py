"""Módulo para gerenciamento de middlewares da API.

Este módulo fornece funções e handlers para gerenciar middlewares,
incluindo tratamento de erros e logging.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..exceptions import (
    DocumentNotFoundError,
    InvalidDocumentError,
    InvalidQueryError,
    StorageError,
    UnauthorizedError,
)


def add_error_handler(app: FastAPI) -> None:
    """Adiciona handlers de erro à aplicação.

    Parameters
    ----------
    app : FastAPI
        Aplicação FastAPI para adicionar os handlers.

    """
    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request,
        exc: DocumentNotFoundError
    ) -> JSONResponse:
        """Trata erros de documento não encontrado.

        Parameters
        ----------
        request : Request
            Requisição que gerou o erro.
        exc : DocumentNotFoundError
            Exceção capturada.

        Returns
        -------
        JSONResponse
            Resposta com detalhes do erro.

        """
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidDocumentError)
    async def invalid_document_handler(
        request: Request,
        exc: InvalidDocumentError
    ) -> JSONResponse:
        """Trata erros de documento inválido.

        Parameters
        ----------
        request : Request
            Requisição que gerou o erro.
        exc : InvalidDocumentError
            Exceção capturada.

        Returns
        -------
        JSONResponse
            Resposta com detalhes do erro.

        """
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidQueryError)
    async def invalid_query_handler(
        request: Request,
        exc: InvalidQueryError
    ) -> JSONResponse:
        """Trata erros de consulta inválida.

        Parameters
        ----------
        request : Request
            Requisição que gerou o erro.
        exc : InvalidQueryError
            Exceção capturada.

        Returns
        -------
        JSONResponse
            Resposta com detalhes do erro.

        """
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(StorageError)
    async def storage_error_handler(
        request: Request,
        exc: StorageError
    ) -> JSONResponse:
        """Trata erros de armazenamento.

        Parameters
        ----------
        request : Request
            Requisição que gerou o erro.
        exc : StorageError
            Exceção capturada.

        Returns
        -------
        JSONResponse
            Resposta com detalhes do erro.

        """
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        request: Request,
        exc: UnauthorizedError
    ) -> JSONResponse:
        """Trata erros de autorização.

        Parameters
        ----------
        request : Request
            Requisição que gerou o erro.
        exc : UnauthorizedError
            Exceção capturada.

        Returns
        -------
        JSONResponse
            Resposta com detalhes do erro.

        """
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}
        )
