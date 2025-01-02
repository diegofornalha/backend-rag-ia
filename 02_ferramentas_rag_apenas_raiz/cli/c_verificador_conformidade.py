#!/usr/bin/env python3
"""
Ferramenta CLI para verificar a conformidade do projeto.
Analisa código fonte, SQL e configurações em busca de inconsistências.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

class VerificadorConformidade:
    """Classe principal para verificação de conformidade."""
    
    def __init__(self):
        """Inicializa o verificador."""
        self.problemas: list[dict] = []
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
    
    def verificar_arquivo(self, arquivo: Path) -> list[dict]:
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
    
    def verificar_json(self, arquivo: Path, conteudo: str, problemas: list[dict]) -> None:
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
    
    def verificar_yaml(self, arquivo: Path, conteudo: str, problemas: list[dict]) -> None:
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
    
    def _verificar_dict_recursivo(self, dados: dict, arquivo: Path, problemas: list[dict]) -> None:
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
            console.print("\n[red]Erro ao verificar diretório %s: %s[/red]", diretorio, str(e))
    
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
        problemas_por_tipo = {}
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
    
    def gerar_embate(self) -> dict:
        """Gera um embate com os problemas encontrados e recomendações."""
        tipos_problemas = {p['tipo'] for p in self.problemas}
        
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
                "Foram verificados:\n"
                f"- {self.diretorios_verificados} diretórios\n"
                f"- {self.arquivos_verificados} arquivos\n"
                f"- Encontrados {len(self.problemas)} problemas\n\n"
                "Tipos de problemas encontrados:\n"
                + "\n".join(f"- {tipo}" for tipo in tipos_problemas)
            ),
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [],
            "arquivo": f"embate_conformidade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
        
        # Adiciona argumentos com recomendações
        for tipo in tipos_problemas:
            if tipo in recomendacoes:
                embate["argumentos"].append({
                    "autor": "verificador_conformidade",
                    "tipo": "tecnico",
                    "conteudo": (
                        f"Recomendações para correção de problemas do tipo '{tipo}':\n\n"
                        f"{recomendacoes[tipo]}"
                    ),
                    "data": datetime.now().isoformat()
                })
        
        return embate

def main() -> None:
    """Função principal."""
    try:
        console.print("\n[bold]🔍 Verificador de Conformidade[/bold]")
        
        # Inicializa verificador
        verificador = VerificadorConformidade()
        
        # Obtém diretório atual
        diretorio = Path.cwd()
        
        # Inicia verificação com spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Verificando projeto...", total=None)
            verificador.verificar_diretorio(diretorio)
        
        # Exibe relatório
        verificador.exibir_relatorio()
        
        # Gera embate se houver problemas
        if verificador.problemas:
            embate = verificador.gerar_embate()
            
            # Salva embate
            arquivo_embate = Path(embate["arquivo"])
            with open(arquivo_embate, "w") as f:
                json.dump(embate, f, indent=2)
                
            console.print(f"\n[green]✅ Embate salvo em: {arquivo_embate}[/green]")
        
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Verificação cancelada![/bold]")
    except Exception as e:
        console.print("\n[red]Erro inesperado: %s[/red]", str(e))

if __name__ == "__main__":
    main() 