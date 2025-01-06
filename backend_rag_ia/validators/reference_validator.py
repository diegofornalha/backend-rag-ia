from typing import Dict, List, Optional, Set
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReferenceValidationError(Exception):
    """Erro de validação de referência"""

    pass


class ReferenceValidator:
    """Validador de referências entre embates"""

    def __init__(self, embates_dir: str):
        """
        Inicializa o validador

        Args:
            embates_dir: Diretório base dos embates
        """
        self.embates_dir = Path(embates_dir)
        self._cache = {}  # Cache de embates carregados

    def _load_embate(self, embate_id: str) -> Optional[Dict]:
        """
        Carrega um embate do disco

        Args:
            embate_id: ID do embate

        Returns:
            Dicionário com dados do embate ou None se não encontrar
        """
        try:
            # Verifica cache
            if embate_id in self._cache:
                return self._cache[embate_id]

            # Procura arquivo
            for file in self.embates_dir.glob("**/*.json"):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        if data.get("id") == embate_id:
                            self._cache[embate_id] = data
                            return data
                except Exception as e:
                    logger.warning(f"Erro ao ler arquivo {file}: {str(e)}")

            return None

        except Exception as e:
            logger.error(f"Erro ao carregar embate {embate_id}: {str(e)}")
            return None

    def _extract_references(self, content: str) -> Set[str]:
        """
        Extrai IDs de embates referenciados em um texto

        Args:
            content: Texto a ser analisado

        Returns:
            Conjunto de IDs encontrados
        """
        import re

        # Padrão: #ID ou [ID] ou (ID)
        pattern = r"(?:^|\s)(?:#|\[|\()([a-f0-9-]{36})(?:\]|\)|\s|$)"

        matches = re.finditer(pattern, content, re.IGNORECASE)
        return {match.group(1) for match in matches}

    def get_references(self, embate: Dict) -> Set[str]:
        """
        Obtém todas as referências em um embate

        Args:
            embate: Dicionário com dados do embate

        Returns:
            Conjunto de IDs referenciados
        """
        references = set()

        # Verifica contexto
        if "contexto" in embate:
            references.update(self._extract_references(embate["contexto"]))

        # Verifica argumentos
        for arg in embate.get("argumentos", []):
            if "conteudo" in arg:
                references.update(self._extract_references(arg["conteudo"]))

        return references

    def get_reverse_references(self, embate_id: str) -> List[Dict]:
        """
        Obtém embates que referenciam um determinado embate

        Args:
            embate_id: ID do embate

        Returns:
            Lista de embates que referenciam o ID
        """
        references = []

        try:
            # Procura em todos os arquivos
            for file in self.embates_dir.glob("**/*.json"):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        if data.get("id") != embate_id:  # Ignora auto-referência
                            refs = self.get_references(data)
                            if embate_id in refs:
                                references.append(data)
                except Exception as e:
                    logger.warning(f"Erro ao ler arquivo {file}: {str(e)}")

            return references

        except Exception as e:
            logger.error(f"Erro ao buscar referências reversas para {embate_id}: {str(e)}")
            return []

    def validate_references(self, embate: Dict) -> List[str]:
        """
        Valida referências em um embate

        Args:
            embate: Dicionário com dados do embate

        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []

        try:
            # Obtém referências
            references = self.get_references(embate)

            # Valida cada referência
            for ref_id in references:
                ref_embate = self._load_embate(ref_id)
                if not ref_embate:
                    errors.append(f"Referência não encontrada: {ref_id}")
                    continue

                # Valida estado
                if ref_embate.get("status") == "fechado":
                    continue  # Referências a embates fechados são sempre válidas

                # Valida ciclo
                if embate.get("id") in self.get_references(ref_embate):
                    errors.append(
                        f"Referência cíclica detectada entre " f"{embate.get('id')} e {ref_id}"
                    )

            return errors

        except Exception as e:
            logger.error(f"Erro ao validar referências: {str(e)}")
            return [f"Erro ao validar referências: {str(e)}"]

    def check_orphaned_references(self) -> List[Dict]:
        """
        Verifica referências órfãs no sistema

        Returns:
            Lista de problemas encontrados
        """
        problems = []

        try:
            # Mapeia todos os embates
            embates = {}
            for file in self.embates_dir.glob("**/*.json"):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        if "id" in data:
                            embates[data["id"]] = data
                except Exception as e:
                    logger.warning(f"Erro ao ler arquivo {file}: {str(e)}")

            # Verifica referências
            for embate_id, embate in embates.items():
                references = self.get_references(embate)
                for ref_id in references:
                    if ref_id not in embates:
                        problems.append(
                            {
                                "tipo": "referencia_nao_encontrada",
                                "embate_origem": embate_id,
                                "referencia": ref_id,
                            }
                        )
                    elif embates[ref_id].get("status") == "fechado":
                        continue  # Referências a embates fechados são válidas
                    else:
                        # Verifica ciclos
                        visited = {embate_id}
                        current = ref_id
                        while True:
                            if current in visited:
                                problems.append(
                                    {"tipo": "ciclo_detectado", "embates": list(visited)}
                                )
                                break

                            visited.add(current)
                            next_refs = self.get_references(embates[current])

                            if not next_refs:
                                break

                            current = next(iter(next_refs))

            return problems

        except Exception as e:
            logger.error(f"Erro ao verificar referências órfãs: {str(e)}")
            return [{"tipo": "erro", "mensagem": f"Erro ao verificar referências órfãs: {str(e)}"}]

    def get_reference_graph(self, embate_id: str) -> Dict:
        """
        Gera grafo de referências para um embate

        Args:
            embate_id: ID do embate raiz

        Returns:
            Dicionário com estrutura do grafo
        """
        try:
            graph = {"nodes": [], "edges": []}

            visited = set()
            queue = [(embate_id, None)]  # (id, parent_id)

            while queue:
                current_id, parent_id = queue.pop(0)

                if current_id in visited:
                    continue

                visited.add(current_id)

                # Carrega embate
                embate = self._load_embate(current_id)
                if not embate:
                    continue

                # Adiciona nó
                graph["nodes"].append(
                    {
                        "id": current_id,
                        "titulo": embate.get("titulo", "Sem título"),
                        "tipo": embate.get("tipo", "desconhecido"),
                        "status": embate.get("status", "desconhecido"),
                    }
                )

                # Adiciona aresta
                if parent_id:
                    graph["edges"].append({"source": parent_id, "target": current_id})

                # Adiciona referências à fila
                references = self.get_references(embate)
                for ref_id in references:
                    if ref_id not in visited:
                        queue.append((ref_id, current_id))

            return graph

        except Exception as e:
            logger.error(f"Erro ao gerar grafo de referências para {embate_id}: {str(e)}")
            return {"nodes": [], "edges": []}
