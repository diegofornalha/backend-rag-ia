#!/usr/bin/env python3

import click
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

# Novo caminho para o diretório de embates
REGISTRO_EMBATES = Path("02_ferramentas_rag_apenas_raiz/dados_embates")
REGISTRO_EMBATES.mkdir(parents=True, exist_ok=True)

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
    
    async def agrupar_por_tema(self, embates: List[Embate]) -> Dict[str, List[Embate]]:
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
                self.logger.error(f"Erro ao processar {embate.arquivo}", 
                                extra={"error": str(e)}, exc_info=True)
    
    async def processar(self) -> List[Path]:
        """
        Processa todos os embates, gerando arquivos de regras quando apropriado.
        
        Returns:
            Lista de arquivos de regras gerados
        """
        self.logger.info("Iniciando processamento de embates", 
                        extra={"dir_embates": str(self.dir_embates)})
        
        # Verifica status do sistema
        if not self.verificar_status_sistema():
            self.logger.error("Sistema indisponível")
            return []
        
        arquivos_gerados = []
        
        try:
            # Carrega e agrupa embates
            embates = self.carregar_embates()
            grupos = await self.agrupar_por_tema(embates)
            
            # Processa cada grupo com embates suficientes
            for tema, embates_tema in grupos.items():
                if len(embates_tema) >= self.min_embates_tema:
                    # Gera e salva regras
                    conteudo = self.gerar_regras_md(tema, embates_tema)
                    arquivo = self.salvar_regras(tema, conteudo)
                    arquivos_gerados.append(arquivo)
                    
                    # Remove embates processados
                    self.arquivar_embates(embates_tema)
                    
                    # Sincroniza com Supabase se configurado
                    if self.auto_sync:
                        await self.sincronizar_com_supabase(arquivo, tema, embates_tema)
            
            self.logger.info("Processamento concluído",
                           extra={"arquivos_gerados": [str(a) for a in arquivos_gerados]})
            return arquivos_gerados
            
        except Exception as e:
            self.logger.error("Erro no processamento",
                            extra={"error": str(e)}, exc_info=True)
            raise

@click.group()
def cli():
    """Ferramenta para gerenciar embates saudáveis no projeto."""
    pass

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título descritivo do embate")
@click.option("--tipo", type=click.Choice(["preferencia", "tecnico"]), prompt="Tipo do embate")
@click.option("--contexto", prompt="Contexto do embate", help="Descrição detalhada do contexto")
def iniciar(titulo: str, tipo: str, contexto: str):
    """Inicia um novo embate."""
    try:
        # Cria novo embate
        embate = Embate(
            titulo=titulo,
            tipo=tipo,
            contexto=contexto,
            status="aberto",
            data_inicio=datetime.now(),
            argumentos=[],
            decisao=None,
            razao=None,
            arquivo=f"embate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Salva em arquivo
        arquivo = REGISTRO_EMBATES / embate.arquivo
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(embate.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Embate iniciado: {titulo}")
        
        click.echo(f"\n✅ Embate iniciado: {titulo}\n")
        click.echo("Próximos passos:")
        click.echo("1. Use 'adicionar-argumento' para registrar argumentos")
        click.echo("2. Use 'resolver' quando chegar a uma conclusão")
        click.echo("3. Use 'listar' para ver todos os embates")
        
    except Exception as e:
        logger.error(f"Erro ao iniciar embate: {str(e)}")
        click.echo(f"❌ Erro ao iniciar embate: {str(e)}")

@cli.command()
@click.option("--titulo", required=True, help="Título do embate")
@click.option("--autor", required=True, help="Autor do argumento")
@click.option("--tipo", required=True, type=click.Choice(["tecnico", "preferencia"]), help="Tipo do argumento")
@click.option("--conteudo", required=True, help="Conteúdo do argumento")
def adicionar_argumento(titulo: str, autor: str, tipo: str, conteudo: str):
    """Adiciona um argumento a um embate existente."""
    try:
        # Encontra o arquivo do embate
        arquivos = list(REGISTRO_EMBATES.glob("embate_*.json"))
        arquivo_embate = None
        
        for arquivo in arquivos:
            with open(arquivo) as f:
                dados = json.load(f)
                if dados["titulo"] == titulo:
                    arquivo_embate = arquivo
                    break
        
        if not arquivo_embate:
            raise ValueError(f"Embate não encontrado: {titulo}")
            
        # Carrega embate
        with open(arquivo_embate) as f:
            dados = json.load(f)
            embate = Embate(**dados)
            
        # Adiciona argumento
        argumento = Argumento(
            autor=autor,
            tipo=tipo,
            conteudo=conteudo,
            data=datetime.now()
        )
        embate.argumentos.append(argumento)
        
        # Salva atualização
        with open(arquivo_embate, "w", encoding="utf-8") as f:
            json.dump(embate.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Argumento adicionado ao embate: {titulo}")
        
        click.echo(f"\n✅ Argumento adicionado ao embate: {titulo}\n")
        click.echo("Próximos passos:")
        click.echo("1. Adicione mais argumentos se necessário")
        click.echo("2. Use 'resolver' quando chegar a uma conclusão")
        click.echo("3. Use 'listar' para ver todos os embates")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar argumento: {str(e)}")
        click.echo(f"❌ Erro ao adicionar argumento: {str(e)}")

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título do embate para resolver")
@click.option("--decisao", prompt="Decisão final", help="A decisão tomada")
@click.option("--razao", prompt="Razão da decisão", help="Justificativa da decisão")
def resolver(titulo: str, decisao: str, razao: str):
    """Resolve um embate existente."""
    for arquivo in REGISTRO_EMBATES.glob("embate_*.json"):
        with open(arquivo) as f:
            dados = json.load(f)
            if dados["titulo"] == titulo and dados["status"] == "aberto":
                dados["status"] = "resolvido"
                dados["decisao"] = decisao
                dados["razao"] = razao
                dados["data_resolucao"] = datetime.now().isoformat()
                
                with open(arquivo, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
                
                # Gerar registro no formato markdown
                registro_md = f"""## Decisão: {titulo}

- Tipo: {dados['tipo']}
- Contexto: {dados['contexto']}
- Data Início: {dados['data_inicio']}
- Data Resolução: {dados['data_resolucao']}

### Argumentos:

{chr(10).join([f"- **{arg['autor']}** ({arg['tipo']}): {arg['conteudo']}" for arg in dados['argumentos']])}

### Decisão Final
{decisao}

### Razão
{razao}
"""
                
                # Salvar no arquivo de registro de decisões
                registro_path = Path("01_regras_md_apenas_raiz/1_core/j_registro_decisoes.md")
                if registro_path.exists():
                    with open(registro_path, "a", encoding="utf-8") as f:
                        f.write(f"\n\n{registro_md}")
                
                logger.info(f"Embate resolvido: {titulo}")
                click.echo(f"\n✅ Embate resolvido: {titulo}")
                click.echo("\nRegistro adicionado ao arquivo de decisões")
                return
    
    logger.warning(f"Embate não encontrado ou já fechado: {titulo}")
    click.echo("❌ Embate não encontrado ou já fechado")

@cli.command()
@click.option("--status", type=click.Choice(["aberto", "resolvido", "todos"]), default="todos", help="Filtrar por status")
def listar(status: str):
    """Lista todos os embates registrados."""
    embates = []
    for arquivo in REGISTRO_EMBATES.glob("embate_*.json"):
        with open(arquivo) as f:
            dados = json.load(f)
            embates.append(dados)
    
    if not embates:
        logger.warning("Nenhum embate registrado")
        click.echo("Nenhum embate registrado")
        return
    
    for embate in embates:
        if status == "todos" or embate["status"] == status:
            click.echo(f"\n📌 {embate['titulo']}")
            click.echo(f"Status: {embate['status']}")
            click.echo(f"Tipo: {embate['tipo']}")
            click.echo(f"Contexto: {embate['contexto']}")
            if embate["argumentos"]:
                click.echo("\nArgumentos:")
                for arg in embate["argumentos"]:
                    click.echo(f"- {arg['autor']}: {arg['conteudo']} ({arg['tipo']})")
            if embate["status"] == "resolvido":
                click.echo(f"\nDecisão: {embate['decisao']}")
                click.echo(f"Razão: {embate['razao']}")
            click.echo("-" * 50)

async def main():
    """Função principal para execução via CLI."""
    condensador = CondensadorEmbates()
    try:
        arquivos = await condensador.processar()
        
        logger.info("Processamento concluído!")
        click.echo(f"\nProcessamento concluído!")
        click.echo(f"Arquivos de regras gerados:")
        for arquivo in arquivos:
            click.echo(f"- {arquivo}")
    except Exception as e:
        logger.error("Erro na execução", extra={"error": str(e)}, exc_info=True)
        click.echo(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    import sys
    import asyncio
    
    if len(sys.argv) > 1:
        # Se houver argumentos, executa os comandos CLI
        cli()
    else:
        # Se não houver argumentos, executa o processamento assíncrono
        asyncio.run(main()) 