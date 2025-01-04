"""Módulo de configuração da aplicação.

Este módulo fornece funções e classes para configurar a aplicação,
incluindo conexão com Supabase e outras configurações do sistema.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client


def get_supabase_client() -> Client:
    """Cria e retorna um cliente Supabase configurado.

    Returns
    -------
    Client
        Cliente Supabase configurado.

    Raises
    ------
    ValueError
        Se as variáveis de ambiente necessárias não estiverem definidas.
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    """
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias")

    return create_client(url, key)
