# Ferramentas CLI para RAG

Este diretório contém ferramentas de linha de comando para interagir com o sistema RAG.

## Estrutura do Projeto

O projeto segue uma estrutura organizada onde diretórios com sufixo `_apenas_raiz` são consolidados na raiz:

```
/
├── logs/           # Logs da aplicação
├── monitoring/     # Scripts de monitoramento
├── regras_md/     # Documentação em markdown
├── scripts/       # Scripts utilitários
├── sql/          # Scripts SQL e migrações
├── testes/       # Testes automatizados
└── tools/        # Ferramentas CLI (consolida ferramentas_rag)
    ├── cli/      # Ferramentas de linha de comando
    ├── database/ # Ferramentas de banco de dados
    └── utils/    # Utilitários compartilhados
```

## Ferramentas Disponíveis

### 1. Busca Semântica com IA

A ferramenta `d_busca_semantica_com_ia.py` oferece uma interface conversacional para realizar buscas semânticas com processamento LLM.

### 2. Busca Semântica Simples

A ferramenta `c_busca_semantica_simples.py` permite realizar buscas semânticas diretas sem processamento LLM.

### 3. Upload de Documentos

A ferramenta `b_subir_para_supabase.py` faz upload de documentos markdown para o Supabase.

### 4. Limpeza do Banco

A ferramenta `a_limpar_banco.py` permite limpar a tabela de documentos no Supabase.

## Configuração

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente no arquivo `.env`:

```env
# URL da API (use uma das opções)
LOCAL_URL=http://localhost:10000  # Para desenvolvimento local
ACTIVE_URL=https://sua-api.com    # Para produção

# Versão da API (opcional)
API_VERSION=v1

# Chave da API do Gemini
GEMINI_API_KEY=sua-chave-aqui

# Credenciais do Supabase
SUPABASE_URL=sua-url-aqui
SUPABASE_SERVICE_KEY=sua-chave-aqui

# Diretório de documentos (opcional)
DOCS_DIR=docs
```

## Uso

Cada ferramenta pode ser executada diretamente:

```bash
# Busca semântica com IA
python d_busca_semantica_com_ia.py

# Busca semântica simples
python c_busca_semantica_simples.py

# Upload de documentos
python b_subir_para_supabase.py

# Limpeza do banco
python a_limpar_banco.py
```

## Funcionalidades Comuns

- Interface amigável via linha de comando
- Formatação rica das saídas
- Tratamento de erros robusto
- Feedback visual do progresso
- Confirmação para operações críticas
