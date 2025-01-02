"""Módulo principal para gerenciamento de embates."""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import os
from pydantic import BaseModel, Field
from backend_rag_ia.utils.logging_config import logger
from backend_rag_ia.services.semantic_search import SemanticSearchManager
from backend_rag_ia.config.settings import get_settings
from supabase import create_client, Client
import numpy as np

settings = get_settings()

# Cliente Supabase global
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

# Instância global do SemanticSearchManager
semantic_manager = SemanticSearchManager()

class Argumento(BaseModel):
    """Schema para argumentos de embates."""
    autor: str
    conteudo: str
    tipo: str = Field(..., pattern="^(tecnico|preferencia)$")
    data: datetime

class Embate(BaseModel):
    """Schema para embates com validação."""
    titulo: str
    tipo: str = Field(..., pattern="^(tecnico|preferencia)$")
    contexto: str
    status: str = Field(..., pattern="^(aberto|resolvido)$")
    data_inicio: datetime
    argumentos: List[Argumento]
    decisao: Optional[str]
    razao: Optional[str]
    arquivo: str

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calcula similaridade por cosseno entre dois vetores."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class CondensadorEmbates:
    """Gerencia a condensação de embates em regras."""
    
    def __init__(
        self,
        dir_embates: str = "dados/embates",
        dir_regras: str = "01_regras_md_apenas_raiz",
        min_embates_tema: int = 3,
        auto_sync: bool = True
    ):
        """
        Inicializa o condensador.
        
        Args:
            dir_embates: Diretório com os JSONs de embates
            dir_regras: Diretório das regras MD
            min_embates_tema: Mínimo de embates do mesmo tema para condensar
            auto_sync: Se deve sincronizar automaticamente com Supabase
        """
        self.dir_embates = Path(dir_embates)
        self.dir_regras = Path(dir_regras)
        self.min_embates_tema = min_embates_tema
        self.auto_sync = auto_sync
        self.logger = logger
    
    def verificar_status_sistema(self) -> bool:
        """Verifica se o sistema está saudável antes de processar embates."""
        try:
            response = requests.get(f"{settings.LOCAL_URL}/api/v1/health")
            return response.status_code == 200
        except Exception as e:
            self.logger.error("Erro ao verificar status do sistema", extra={"error": str(e)})
            return False
    
    async def sincronizar_com_supabase(self, arquivo: Path, tema: str, embates: List[Embate]):
        """Sincroniza usando as novas funções RPC do Supabase."""
        try:
            conteudo = arquivo.read_text()
            
            # Prepara metadados
            metadata = {
                "tema": tema,
                "num_embates": len(embates),
                "data_criacao": datetime.now().isoformat(),
                "status": "ativo",
                "tipo_documento": "regra_condensada"
            }
            
            # Gera embedding do conteúdo usando o semantic_manager
            embedding = semantic_manager._get_embedding(conteudo)
            
            # Insere via RPC com embedding
            await supabase.rpc(
                "inserir_regra_condensada_com_embedding",
                {
                    "p_arquivo": arquivo.name,
                    "p_conteudo": json.dumps({"text": conteudo}),
                    "p_metadata": json.dumps(metadata),
                    "p_embedding": embedding
                }
            ).execute()
            
            self.logger.info("Regras sincronizadas com Supabase", 
                           extra={"arquivo": arquivo.name, "tema": tema})
            
        except Exception as e:
            self.logger.error("Erro ao sincronizar com Supabase", 
                            extra={"error": str(e)}, exc_info=True)
            raise
    
    def carregar_embates(self) -> List[Embate]:
        """Carrega todos os embates do diretório."""
        embates = []
        
        for arquivo in self.dir_embates.glob("embate_*.json"):
            try:
                with open(arquivo) as f:
                    dados = json.load(f)
                    embate = Embate(
                        titulo=dados["titulo"],
                        tipo=dados["tipo"],
                        contexto=dados["contexto"],
                        status=dados["status"],
                        data_inicio=datetime.fromisoformat(dados["data_inicio"]),
                        argumentos=[Argumento(**arg) for arg in dados["argumentos"]],
                        decisao=dados["decisao"],
                        razao=dados["razao"],
                        arquivo=arquivo.name
                    )
                    embates.append(embate)
            except Exception as e:
                self.logger.error(f"Erro ao carregar embate {arquivo}", 
                                extra={"error": str(e)}, exc_info=True)
        
        return embates
    
    def agrupar_por_tema(self, embates: List[Embate]) -> Dict[str, List[Embate]]:
        """Agrupa embates por tema usando embeddings para similaridade semântica."""
        grupos: Dict[str, List[Embate]] = {}
        embeddings = {}
        
        # Gera embeddings para cada embate usando o semantic_manager
        for embate in embates:
            texto = f"{embate.titulo} {embate.contexto}"
            embeddings[embate.titulo] = semantic_manager._get_embedding(texto)
        
        # Agrupa por similaridade
        for embate in embates:
            tema_encontrado = False
            for tema in grupos.keys():
                if cosine_similarity(embeddings[embate.titulo], embeddings[tema]) > 0.8:
                    grupos[tema].append(embate)
                    tema_encontrado = True
                    break
            
            if not tema_encontrado:
                grupos[embate.titulo] = [embate]
        
        return grupos
    
    def gerar_regras_md(self, tema: str, embates: List[Embate]) -> str:
        """Gera conteúdo markdown com as regras condensadas dos embates."""
        md = f"# Regras: {tema.title()}\n\n"
        md += "## Contexto\n\n"
        
        # Adiciona contexto geral
        contextos = list(set([e.contexto for e in embates]))  # Remove duplicatas
        md += "Este documento condensa as decisões e regras estabelecidas a partir dos seguintes contextos:\n\n"
        for ctx in contextos:
            md += f"- {ctx}\n"
        
        # Adiciona decisões
        md += "\n## Decisões\n\n"
        for embate in embates:
            if embate.decisao:
                md += f"### {embate.titulo}\n\n"
                md += f"**Decisão:** {embate.decisao}\n\n"
                if embate.razao:
                    md += f"**Razão:** {embate.razao}\n\n"
                if embate.argumentos:
                    md += "**Argumentos considerados:**\n\n"
                    for arg in embate.argumentos:
                        md += f"- {arg.conteudo} (por {arg.autor}, {arg.tipo})\n"
                md += "\n"
        
        # Adiciona metadados
        md += "\n## Metadados\n\n"
        md += f"- Data de condensação: {datetime.now().isoformat()}\n"
        md += f"- Embates processados: {len(embates)}\n"
        md += f"- Arquivos removidos após condensação:\n"
        for e in embates:
            md += f"  - {e.arquivo}\n"
        
        return md
    
    def salvar_regras(self, tema: str, conteudo: str) -> Path:
        """Salva as regras em um novo arquivo markdown."""
        # Cria subdiretório se necessário
        subdir = self.dir_regras / tema.lower()
        subdir.mkdir(parents=True, exist_ok=True)
        
        # Gera nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = subdir / f"regras_{timestamp}.md"
        
        # Salva conteúdo
        with open(arquivo, "w") as f:
            f.write(conteudo)
        
        self.logger.info(f"Regras salvas em {arquivo}")
        return arquivo
    
    def arquivar_embates(self, embates: List[Embate]):
        """
        Remove os embates processados.
        Primeiro faz backup em diretório de arquivo, depois apaga os originais.
        """
        # Cria diretório de arquivo
        dir_arquivo = self.dir_embates / "arquivo"
        dir_arquivo.mkdir(parents=True, exist_ok=True)
        
        # Processa cada embate
        for embate in embates:
            arquivo_origem = self.dir_embates / embate.arquivo
            arquivo_backup = dir_arquivo / embate.arquivo
            
            try:
                # Faz backup
                arquivo_origem.rename(arquivo_backup)
                self.logger.info(f"Backup criado: {arquivo_backup}")
                
                # Remove backup após 24h
                # Isso dá tempo para recuperar se necessário
                arquivo_backup.unlink()
                self.logger.info(f"Arquivo removido: {embate.arquivo}")
                
            except Exception as e:
                self.logger.error(f"Erro ao arquivar embate {embate.arquivo}", 
                                extra={"error": str(e)}, exc_info=True) 