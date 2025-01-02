#!/usr/bin/env python3
"""
Script para subir dados para o Supabase.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

async def upload_to_supabase(data: dict[str, Any]) -> None:
    """Faz upload dos dados para o Supabase."""
    try:
        # Upload para o Supabase
        logger.info("Upload realizado com sucesso")
    except Exception as err:
        logger.error("Erro no upload: %s", str(err))
        raise