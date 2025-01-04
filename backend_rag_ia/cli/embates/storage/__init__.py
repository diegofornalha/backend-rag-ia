<<<<<<< Updated upstream
"""Sistema de armazenamento para embates.

Este módulo fornece implementações de armazenamento para embates,
incluindo persistência em arquivo e memória.
"""

import json
from pathlib import Path
from typing import Any, Optional


class EmbateStorage:
    """Armazenamento de embates em sistema de arquivos.

    Esta classe fornece uma implementação de armazenamento de embates
    utilizando o sistema de arquivos local.

    Attributes
    ----------
    base_path : Path
        Caminho base para armazenamento dos arquivos.

    """

    def __init__(self, base_path: str | Path) -> None:
        """Inicializa o armazenamento.

        Parameters
        ----------
        base_path : str | Path
            Caminho base para armazenamento dos arquivos.

        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_embate(self, embate_id: str, data: dict[str, Any]) -> None:
        """Salva um embate no armazenamento.

        Parameters
        ----------
        embate_id : str
            ID do embate a ser salvo.
        data : dict[str, Any]
            Dados do embate a serem salvos.

        """
        file_path = self.base_path / f"{embate_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=str, indent=2)

    def load_embate(self, embate_id: str) -> Optional[dict[str, Any]]:
        """Carrega um embate do armazenamento.

        Parameters
        ----------
        embate_id : str
            ID do embate a ser carregado.

        Returns
        -------
        Optional[dict[str, Any]]
            Dados do embate carregado ou None se não existir.

        """
=======
import json
from pathlib import Path
from typing import Any, Optional


class EmbateStorage:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_embate(self, embate_id: str, data: dict[str, Any]) -> None:
        file_path = self.base_path / f"{embate_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=str, indent=2)

    def load_embate(self, embate_id: str) -> Optional[dict[str, Any]]:
>>>>>>> Stashed changes
        file_path = self.base_path / f"{embate_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)

    def list_embates(self) -> list[str]:
<<<<<<< Updated upstream
        """Lista todos os embates no armazenamento.

        Returns
        -------
        list[str]
            Lista de IDs dos embates armazenados.

        """
        return [f.stem for f in self.base_path.glob("*.json")]

    def delete_embate(self, embate_id: str) -> bool:
        """Remove um embate do armazenamento.

        Parameters
        ----------
        embate_id : str
            ID do embate a ser removido.

        Returns
        -------
        bool
            True se o embate foi removido com sucesso, False caso contrário.

        """
=======
        return [f.stem for f in self.base_path.glob("*.json")]

    def delete_embate(self, embate_id: str) -> bool:
>>>>>>> Stashed changes
        file_path = self.base_path / f"{embate_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
