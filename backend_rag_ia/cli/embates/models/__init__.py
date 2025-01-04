"""Define modelos para embates.

Este módulo define as estruturas de dados básicas para o sistema de embates.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class Argumento:
    """Define um argumento em um embate.

    Parameters
    ----------
    autor : str
        Nome ou identificador do autor do argumento.
    conteudo : str
        Conteúdo do argumento.
    tipo : str
        Tipo do argumento (ex: 'proposta', 'contra-argumento').
    data : datetime
        Data e hora em que o argumento foi criado.
    metadata : dict[str, Any]
        Metadados adicionais do argumento.

    """

    autor: str
    conteudo: str
    tipo: str
    data: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class EmbateBase:
    """Define um embate base para análise de código.

    Parameters
    ----------
    titulo : str
        Título descritivo do embate.
    contexto : str
        Descrição detalhada do contexto do embate.
    tipo : str
        Tipo do embate (ex: 'refatoração', 'bug', 'feature').
    status : str
        Status atual do embate.
    data_inicio : datetime
        Data e hora de início do embate.
    data_resolucao : Optional[datetime]
        Data e hora de resolução do embate, se resolvido.
    argumentos : list[Argumento]
        Lista de argumentos do embate.
    decisao : Optional[str]
        Decisão final do embate, se houver.
    razao : Optional[str]
        Razão da decisão tomada.
    metadata : dict[str, Any]
        Metadados adicionais do embate.

    """

    titulo: str
    contexto: str
    tipo: str = "refatoracao"
    status: str = "aberto"
    data_inicio: datetime = field(default_factory=datetime.now)
    data_resolucao: Optional[datetime] = None
    argumentos: list[Argumento] = field(default_factory=list)
    decisao: Optional[str] = None
    razao: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

# Criar um embate para análise de formatação
embate_formatacao = EmbateBase(
    titulo="Análise e resolução de problemas de formatação de linha longa",
    contexto="""
    Foram identificados múltiplos problemas de formatação no arquivo backend_rag_ia/app/main.py,
    onde várias linhas excedem o limite recomendado de 100 caracteres. Precisamos analisar e
    propor a melhor abordagem para resolver esses problemas mantendo a legibilidade e
    funcionalidade do código.
    """,
    tipo="refatoracao",
    argumentos=[
        Argumento(
            autor="sistema",
            tipo="analise",
            conteudo="""
            Existem três abordagens principais para resolver este problema:
            1. Quebrar as linhas longas em múltiplas linhas usando parênteses ou operadores
            2. Refatorar o código para reduzir naturalmente o comprimento das linhas
            3. Ajustar a configuração do linter para aceitar linhas mais longas
            
            Cada abordagem tem seus prós e contras que precisamos analisar.
            """
        ),
        Argumento(
            autor="sistema",
            tipo="proposta",
            conteudo="""
            Proposta de solução híbrida:
            1. Primeiro, tentar quebrar as linhas longas que são facilmente divisíveis
               (como chamadas de função com muitos parâmetros)
            2. Para casos onde a quebra de linha prejudicaria a legibilidade,
               refatorar o código extraindo variáveis ou funções
            3. Manter o limite de 100 caracteres como padrão para manter consistência
               com as melhores práticas Python (PEP 8)
            """
        ),
        Argumento(
            autor="sistema",
            tipo="implementacao",
            conteudo="""
            Plano de implementação:
            1. Identificar padrões nas linhas longas (são principalmente chamadas de função?)
            2. Criar templates de refatoração para cada padrão identificado
            3. Aplicar as refatorações de forma consistente em todo o arquivo
            4. Adicionar comentários explicativos onde necessário
            5. Verificar se as mudanças não introduziram outros problemas de estilo
            """
        ),
        Argumento(
            autor="sistema",
            tipo="analise_padrao",
            conteudo="""
            Análise dos padrões de linhas longas encontrados no arquivo main.py:
            
            1. Chamadas de método encadeadas do Supabase:
               - Padrão: supabase.table('nome_tabela').select('*').eq('campo', valor).execute()
               - Problema: Múltiplos métodos encadeados em uma única linha
               
            2. Strings de tabela longas:
               - Padrão: 'rag.01_base_conhecimento_regras_geral'
               - Problema: Nomes de tabela muito longos repetidos em várias partes do código
               
            Proposta de refatoração específica:
            
            1. Para chamadas encadeadas:
               ```python
               result = await (
                   supabase.table('rag.01_base_conhecimento_regras_geral')
                   .select('*')
                   .eq('id', document_id)
                   .execute()
               )
               ```
               
            2. Para nomes de tabela:
               ```python
               # Constantes no topo do arquivo
               TABELA_BASE_CONHECIMENTO = 'rag.01_base_conhecimento_regras_geral'
               TABELA_EMBEDDINGS = 'rag.02_embeddings_regras_geral'
               
               # No código
               result = await supabase.table(TABELA_BASE_CONHECIMENTO).select('*')...
               ```
            
            Esta abordagem:
            - Melhora a legibilidade quebrando operações complexas em múltiplas linhas
            - Reduz duplicação através do uso de constantes
            - Facilita manutenção futura (mudança de nomes de tabela em um só lugar)
            - Mantém a funcionalidade intacta
            """
        ),
        Argumento(
            autor="sistema",
            tipo="decisao",
            conteudo="""
            Decisão de implementação:
            
            1. Criar constantes para nomes de tabela e outros valores repetidos
            2. Refatorar todas as chamadas do Supabase usando o padrão de quebra de linha proposto
            3. Documentar o padrão no código para manter consistência
            4. Adicionar testes para garantir que a funcionalidade permanece a mesma
            
            Esta abordagem foi escolhida porque:
            - É consistente com as melhores práticas Python
            - Melhora a manutenibilidade do código
            - Não requer mudanças na configuração do linter
            - Pode ser aplicada de forma consistente em todo o projeto
            """
        )
    ]
)
