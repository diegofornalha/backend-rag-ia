#!/usr/bin/env python3
"""
Ferramenta CLI para verificar a conformidade do projeto.
Analisa código fonte, SQL e configurações em busca de inconsistências.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

class VerificadorConformidade:
    """Classe principal para verificação de conformidade."""
    
    def __init__(self):
        """Inicializa o verificador."""
        self.problemas: List[Dict] = []
        self.arquivos_verificados = 0
        self.diretorios_verificados = 0
        
        # Padrões para verificação
        self.padroes = {
            'schema_publico': r'(table\(["\'])(public\.|documents|embeddings)',
            'supabase_table': r'supabase\.table\(["\'](?!rag\.)',
            'schema_incorreto': r'(CREATE|ALTER|DROP)\s+TABLE(?!\s+rag\.)',
            'policy_incorreta': r'CREATE\s+POLICY(?!\s+ON\s+rag\.)',
        }
        
        # Diretórios a ignorar
        self.ignorar_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}
        
        # Extensões a verificar
        self.extensoes = {'.py', '.sql', '.json', '.yml', '.yaml', '.md'}
    
    def verificar_arquivo(self, arquivo: Path) -> List[Dict]:
        """Verifica um arquivo em busca de problemas de conformidade."""
        problemas = []
        
        try:
            conteudo = arquivo.read_text(encoding='utf-8')
            
            # Verifica cada padrão
            for nome, padrao in self.padroes.items():
                matches = re.finditer(padrao, conteudo, re.MULTILINE)
                for match in matches:
                    problemas.append({
                        'arquivo': str(arquivo),
                        'linha': conteudo.count('\n', 0, match.start()) + 1,
                        'tipo': nome,
                        'trecho': match.group(0),
                        'contexto': conteudo.splitlines()[conteudo.count('\n', 0, match.start())]
                    })
            
            # Verificações específicas por tipo de arquivo
            if arquivo.suffix == '.json':
                self.verificar_json(arquivo, conteudo, problemas)
            elif arquivo.suffix in {'.yml', '.yaml'}:
                self.verificar_yaml(arquivo, conteudo, problemas)
            
        except Exception as e:
            problemas.append({
                'arquivo': str(arquivo),
                'linha': 0,
                'tipo': 'erro_leitura',
                'trecho': str(e),
                'contexto': 'Erro ao ler arquivo'
            })
        
        return problemas
    
    def verificar_json(self, arquivo: Path, conteudo: str, problemas: List[Dict]) -> None:
        """Verifica problemas específicos em arquivos JSON."""
        try:
            dados = json.loads(conteudo)
            
            # Verifica referências a tabelas/schemas
            if isinstance(dados, dict):
                self._verificar_dict_recursivo(dados, arquivo, problemas)
                
        except json.JSONDecodeError as e:
            problemas.append({
                'arquivo': str(arquivo),
                'linha': e.lineno,
                'tipo': 'json_invalido',
                'trecho': e.msg,
                'contexto': 'JSON inválido'
            })
    
    def verificar_yaml(self, arquivo: Path, conteudo: str, problemas: List[Dict]) -> None:
        """Verifica problemas específicos em arquivos YAML."""
        try:
            import yaml
            dados = yaml.safe_load(conteudo)
            
            # Verifica referências a tabelas/schemas
            if isinstance(dados, dict):
                self._verificar_dict_recursivo(dados, arquivo, problemas)
                
        except yaml.YAMLError as e:
            problemas.append({
                'arquivo': str(arquivo),
                'linha': getattr(e, 'problem_mark', {}).get('line', 0),
                'tipo': 'yaml_invalido',
                'trecho': str(e),
                'contexto': 'YAML inválido'
            })
    
    def _verificar_dict_recursivo(self, dados: Dict, arquivo: Path, problemas: List[Dict]) -> None:
        """Verifica recursivamente um dicionário em busca de problemas."""
        for chave, valor in dados.items():
            # Verifica referências a tabelas/schemas nas chaves
            for nome, padrao in self.padroes.items():
                if re.search(padrao, str(chave)):
                    problemas.append({
                        'arquivo': str(arquivo),
                        'linha': 0,
                        'tipo': nome,
                        'trecho': chave,
                        'contexto': f'Chave: {chave}'
                    })
            
            # Verifica valores recursivamente
            if isinstance(valor, dict):
                self._verificar_dict_recursivo(valor, arquivo, problemas)
            elif isinstance(valor, list):
                for item in valor:
                    if isinstance(item, dict):
                        self._verificar_dict_recursivo(item, arquivo, problemas)
    
    def verificar_diretorio(self, diretorio: Path) -> None:
        """Verifica recursivamente um diretório."""
        try:
            for item in diretorio.iterdir():
                # Ignora diretórios específicos
                if item.is_dir():
                    if item.name not in self.ignorar_dirs:
                        self.diretorios_verificados += 1
                        self.verificar_diretorio(item)
                # Verifica apenas arquivos com extensões específicas
                elif item.suffix in self.extensoes:
                    self.arquivos_verificados += 1
                    problemas = self.verificar_arquivo(item)
                    self.problemas.extend(problemas)
                    
        except Exception as e:
            console.print(f"\n[red]Erro ao verificar diretório {diretorio}: {str(e)}[/red]")
    
    def exibir_relatorio(self) -> None:
        """Exibe relatório dos problemas encontrados."""
        console.print("\n[bold]📊 Relatório de Conformidade[/bold]")
        console.print(f"\nDiretórios verificados: {self.diretorios_verificados}")
        console.print(f"Arquivos verificados: {self.arquivos_verificados}")
        console.print(f"Problemas encontrados: {len(self.problemas)}")
        
        if not self.problemas:
            console.print("\n[green]✨ Nenhum problema de conformidade encontrado![/green]")
            return
        
        # Agrupa problemas por tipo
        problemas_por_tipo: Dict[str, List[Dict]] = {}
        for problema in self.problemas:
            tipo = problema['tipo']
            if tipo not in problemas_por_tipo:
                problemas_por_tipo[tipo] = []
            problemas_por_tipo[tipo].append(problema)
        
        # Cria tabela de problemas
        table = Table(title="\nProblemas Encontrados")
        table.add_column("Arquivo", style="cyan")
        table.add_column("Linha", style="magenta")
        table.add_column("Tipo", style="yellow")
        table.add_column("Trecho", style="red")
        table.add_column("Contexto", style="blue")
        
        for tipo, problemas in problemas_por_tipo.items():
            console.print(f"\n[bold]{tipo}[/bold] ({len(problemas)} ocorrências)")
            for p in problemas:
                table.add_row(
                    str(p['arquivo']),
                    str(p['linha']),
                    p['tipo'],
                    p['trecho'],
                    p['contexto']
                )
        
        console.print(table)
    
    def gerar_embate(self) -> Dict:
        """Gera um embate com os problemas encontrados e recomendações."""
        tipos_problemas = set(p['tipo'] for p in self.problemas)
        
        # Mapeamento de recomendações por tipo de problema
        recomendacoes = {
            'schema_publico': (
                "- Sempre use o schema 'rag.' ao invés de 'public'\n"
                "- Substitua referências diretas a 'documents' ou 'embeddings' por 'rag.01_base_conhecimento_regras_geral' e 'rag.02_embeddings_regras_geral'\n"
                "- Atualize queries para incluir o prefixo 'rag.'"
            ),
            'supabase_table': (
                "- Ao usar client.table(), sempre inclua o prefixo 'rag.'\n"
                "- Exemplo: client.table('rag.01_base_conhecimento_regras_geral')\n"
                "- Verifique se todas as chamadas de API incluem o schema correto"
            ),
            'schema_incorreto': (
                "- Em scripts SQL, sempre especifique 'rag.' antes do nome da tabela\n"
                "- Use 'CREATE TABLE rag.nome_tabela'\n"
                "- Use 'ALTER TABLE rag.nome_tabela'\n"
                "- Use 'DROP TABLE rag.nome_tabela'"
            ),
            'policy_incorreta': (
                "- Políticas RLS devem ser criadas no schema 'rag'\n"
                "- Use 'CREATE POLICY nome_policy ON rag.nome_tabela'\n"
                "- Verifique se todas as políticas existentes foram migradas"
            ),
            'erro_leitura': (
                "- Verifique a codificação do arquivo (deve ser UTF-8)\n"
                "- Verifique as permissões de leitura\n"
                "- Verifique se o arquivo não está corrompido"
            ),
            'json_invalido': (
                "- Valide o JSON usando uma ferramenta online\n"
                "- Verifique a sintaxe (vírgulas, chaves, aspas)\n"
                "- Use um formatador de JSON"
            ),
            'yaml_invalido': (
                "- Valide o YAML usando uma ferramenta online\n"
                "- Verifique a indentação\n"
                "- Verifique a sintaxe (listas, dicionários)"
            )
        }
        
        embate = {
            "titulo": "Verificação de Conformidade do Projeto",
            "tipo": "tecnico",
            "status": "aberto" if self.problemas else "resolvido",
            "contexto": (
                "Verificação automática de conformidade do projeto, "
                "buscando inconsistências no uso de schemas, tabelas e configurações.\n\n"
                "Este embate serve como documentação histórica dos problemas encontrados "
                "e como guia para evitar problemas similares no futuro."
            ),
            "argumentos": [
                {
                    "autor": "verificador",
                    "tipo": "analise",
                    "conteudo": (
                        f"Análise realizada em {self.diretorios_verificados} diretórios "
                        f"e {self.arquivos_verificados} arquivos.\n"
                        f"Foram encontrados {len(self.problemas)} problemas de conformidade "
                        f"nos seguintes aspectos: {', '.join(tipos_problemas)}."
                    )
                }
            ],
            "decisao": (
                "Necessário corrigir as inconsistências encontradas" 
                if self.problemas else 
                "Projeto está em conformidade"
            ),
            "razao": (
                "Foram encontrados problemas que podem afetar a consistência do projeto"
                if self.problemas else
                "Todos os arquivos verificados estão seguindo os padrões estabelecidos"
            ),
            "data_inicio": datetime.now().isoformat(),
            "tags": ["conformidade", "verificacao", "qualidade", "schema_rag"],
            "recomendacoes_gerais": [
                "1. Sempre use o schema 'rag' para todas as operações no Supabase",
                "2. Mantenha um padrão consistente de nomenclatura de tabelas",
                "3. Documente alterações de schema em migrations",
                "4. Use ferramentas de lint e formatação de código",
                "5. Execute esta verificação de conformidade regularmente",
                "6. Revise as políticas RLS ao fazer alterações no schema",
                "7. Mantenha backups antes de alterações significativas",
                "8. Teste queries e operações em ambiente de desenvolvimento"
            ]
        }
        
        # Adiciona detalhes dos problemas e recomendações específicas
        if self.problemas:
            detalhes = []
            recomendacoes_especificas = set()
            
            for p in self.problemas:
                detalhes.append(
                    f"- Arquivo: {p['arquivo']}\n"
                    f"  Linha: {p['linha']}\n"
                    f"  Tipo: {p['tipo']}\n"
                    f"  Trecho: {p['trecho']}\n"
                    f"  Contexto: {p['contexto']}"
                )
                
                # Adiciona recomendações específicas para o tipo de problema
                if p['tipo'] in recomendacoes:
                    recomendacoes_especificas.add(recomendacoes[p['tipo']])
            
            embate["argumentos"].append({
                "autor": "verificador",
                "tipo": "detalhes",
                "conteudo": "\n".join(detalhes)
            })
            
            embate["argumentos"].append({
                "autor": "verificador",
                "tipo": "recomendacoes",
                "conteudo": (
                    "Recomendações específicas para os problemas encontrados:\n\n" +
                    "\n\n".join(recomendacoes_especificas)
                )
            })
        
        return embate

def main() -> None:
    """Função principal."""
    try:
        console.print("\n[bold]🔍 Verificador de Conformidade[/bold]")
        
        # Inicializa verificador
        verificador = VerificadorConformidade()
        
        # Obtém diretório raiz do projeto
        raiz = Path(os.getenv("PROJECT_ROOT", "."))
        
        console.print(f"\nIniciando verificação em: {raiz}")
        
        # Executa verificação
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Verificando conformidade...", total=None)
            verificador.verificar_diretorio(raiz)
            progress.update(task, completed=True)
        
        # Exibe relatório
        verificador.exibir_relatorio()
        
        # Gera embate automaticamente
        console.print("\n[bold]📝 Gerando embate com resultados e recomendações...[/bold]")
        embate = verificador.gerar_embate()
        arquivo_embate = raiz / "embates" / "embate_conformidade.json"
        arquivo_embate.parent.mkdir(exist_ok=True)
        
        with open(arquivo_embate, 'w', encoding='utf-8') as f:
            json.dump(embate, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n[green]✅ Embate gerado em: {arquivo_embate}[/green]")
        console.print("\n[bold]ℹ️ O embate inclui recomendações para prevenir problemas similares no futuro[/bold]")
        
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Verificação cancelada![/bold]")
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {str(e)}[/red]")

if __name__ == "__main__":
    main() 