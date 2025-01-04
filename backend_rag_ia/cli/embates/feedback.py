<<<<<<< Updated upstream
"""Implementa sistema de feedback para embates.
=======
"""Sistema de feedback para embates.
>>>>>>> Stashed changes

Este módulo implementa funcionalidades para coletar e processar feedback
dos usuários sobre os embates, permitindo melhorar a qualidade das respostas.
"""

<<<<<<< Updated upstream
from datetime import datetime
from typing import Any, Optional


class FeedbackEvent:
    """Define um evento de feedback do usuário.
=======
from typing import Any, Optional
from datetime import datetime

class FeedbackEvent:
    """Representa um evento de feedback do usuário.
>>>>>>> Stashed changes

    Esta classe fornece a estrutura para armazenar e processar feedback
    dos usuários sobre os embates.

    Attributes
    ----------
    embate_id : str
        O ID do embate que recebeu o feedback.
    tipo : str
        O tipo de feedback (positivo, negativo, sugestão, etc.).
    conteudo : str
        O conteúdo do feedback fornecido pelo usuário.
    timestamp : datetime
        O momento em que o feedback foi registrado.

    """

    def __init__(self,
                 embate_id: str,
                 tipo: str,
                 conteudo: str,
                 timestamp: Optional[datetime] = None):
        """Inicializa um novo evento de feedback.

        Parameters
        ----------
        embate_id : str
            O ID do embate que recebeu o feedback.
        tipo : str
            O tipo de feedback (positivo, negativo, sugestão, etc.).
        conteudo : str
            O conteúdo do feedback fornecido pelo usuário.
        timestamp : Optional[datetime], optional
            O momento em que o feedback foi registrado, por padrão None.

        """
        self.embate_id = embate_id
        self.tipo = tipo
        self.conteudo = conteudo
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, Any]:
<<<<<<< Updated upstream
        """Retorna o evento de feedback como um dicionário.
=======
        """Converter o evento de feedback em um dicionário.
>>>>>>> Stashed changes

        Returns
        -------
        dict[str, Any]
            O evento de feedback convertido em formato de dicionário.

        """
        return {
            "embate_id": self.embate_id,
            "tipo": self.tipo,
            "conteudo": self.conteudo,
            "timestamp": self.timestamp.isoformat()
        }
