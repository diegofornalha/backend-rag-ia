# Regras do Projeto

## Gerenciamento de Regras

### Organização das Regras

1. **Localização das Regras**:

   - Todas as regras devem estar na pasta `backend_rag_ia/regras_md/`
   - Não criar novas pastas para regras
   - Não duplicar pastas de regras

2. **Adicionando Novas Regras**:

   - Quando receber instrução para "colocar" regras:
     - Adicionar no arquivo `.md` correspondente em `regras_md/`
     - Não criar nova pasta, usar a estrutura existente
   - Para temas completamente novos:
     - Criar novo arquivo `.md` dentro de `regras_md/`
     - Seguir padrão de nomenclatura: `REGRAS_NOVO_TEMA.md`

### Boas Práticas

1. **Manutenção**:

   - Manter regras organizadas por tema
   - Atualizar arquivos existentes ao invés de criar novos
   - Evitar duplicação de informações

2. **Nomenclatura**:

   - Usar MAIÚSCULAS para nomes de arquivos
   - Prefixo "REGRAS\_" para arquivos de regras
   - Sufixo ".md" para todos os arquivos

3. **Conteúdo**:
   - Manter formatação Markdown consistente
   - Organizar regras hierarquicamente
   - Incluir exemplos quando necessário

## 1. Estrutura de Diretórios

### 1.1 Arquivos na Raiz

- **Dockerfile** → Build da aplicação
- **requirements.txt** → Dependências Python
- **render.yaml** → Configurações do Render (opcional)

### 1.2 Scripts e Testes na Raiz

#### Scripts Permitidos na Raiz (`/scripts_apenas_raiz/`)

- Scripts de infraestrutura (Docker, Render, SSH)
- Scripts de monitoramento de produção
- Scripts de formatação e linting
- Scripts de inicialização geral

#### Nomenclatura dos Scripts na Raiz

- Nomes devem ser curtos e autoexplicativos
- Usar snake_case para arquivos Python e kebab-case para Shell
- Usar verbos no infinitivo para indicar ação
- Exemplos:
  - `formatar.py` → Formatador de código
  - `monitorar_docker.py` → Monitoramento de build Docker
  - `verificar_prod.py` → Verificador de produção
  - `controlar_render.py` → Controlador do Render
  - `controlar_ssh.sh` → Controlador de SSH
  - `iniciar.sh` → Inicializador do ambiente

**Não permitido na raiz:**

- Scripts específicos do projeto (devem ficar em `backend_rag_ia/scripts/`)
- Scripts de processamento de dados
- Scripts de regras de negócio

#### Testes na Raiz (`/tests_apenas_raiz/`)

- Testes de infraestrutura
- Testes de deploy
- Testes de configuração

**Não permitido na raiz:**

- Testes unitários do projeto (devem estar em `backend_rag_ia/tests/`)
- Testes de regras de negócio
- Testes de API específicos

### 1.3 Organização de Pastas

- **/regras_md** → Documentação e regras do projeto
- **/monitoring** → Configurações de monitoramento
- **/api** → Código da API
- **/services** → Serviços da aplicação
- **/scripts** → Scripts utilitários

### 1.4 Mudanças em Diretórios

#### Regras de Refatoração de Diretórios

1. **Mudança de Nome ou Localização**:

   - Ao renomear ou mover um diretório, todos os arquivos que o referenciam devem ser atualizados
   - Scripts devem verificar e alertar sobre referências quebradas
   - Exemplo: Se `backend-rag-ia` → `backend_rag_ia`, todos os imports devem ser atualizados

2. **Verificações Obrigatórias**:

   - Antes de commitar mudanças em diretórios:
     - Rodar verificador de imports quebrados
     - Atualizar paths em scripts de configuração
     - Verificar referências em arquivos de build (Dockerfile, etc)

3. **Documentação**:
   - Registrar mudanças significativas no CHANGELOG.md
   - Atualizar documentação que referencia os diretórios
   - Comunicar mudanças para a equipe

**Não permitido:**

- Mover/renomear diretórios sem atualizar referências
- Deixar imports quebrados no código
- Ignorar alertas de paths inválidos

## 2. Padrões de Código

### 2.1 Python

- Usar Python 3.11+
- Seguir PEP 8
- Documentar funções e classes
- Usar type hints

### 2.2 Docker

- Multi-stage builds
- Imagens slim
- Limpar caches
- Healthchecks configurados

### 2.3 API

- Endpoints versionados
- Documentação Swagger
- Validação de dados
- Tratamento de erros

### 2.4 Linting para ML/IA

#### Configuração do Flake8

1. **Regras Específicas para ML**:

   - Permite linhas mais longas em arquivos de modelo
   - Mais flexível com complexidade em código de treino
   - Permite variáveis não utilizadas (útil para tensores)
   - Ignora imports fora de ordem em notebooks

2. **Diretórios Especiais**:

   - `/models/`: Regras flexíveis para definições de modelo
   - `/transformers/`: Permite nomes curtos de variáveis
   - `/preprocessing/`: Mais permissivo com complexidade
   - `/notebooks/`: Ignora maioria das regras de estilo

3. **Docstrings**:

   - Formato Google obrigatório
   - Documentação de parâmetros ML clara
   - Exemplos de uso quando relevante
   - Descrição de shapes de tensores

4. **Exceções Permitidas**:
   - Variáveis não utilizadas em callbacks
   - Imports condicionais para otimização
   - Linhas longas em definição de arquitetura
   - Complexidade alta em loops de treino

## 3. Ambiente de Desenvolvimento

### 3.1 Dependências

- Manter requirements.txt atualizado
- Usar versões específicas
- Documentar dependências opcionais
- Separar dev e prod requirements

### 3.2 Variáveis de Ambiente

- Sempre verificar se o `.env` está configurado antes de rodar scripts
- Usar .env para desenvolvimento
- Nunca commitar .env
- Documentar todas as variáveis
- Usar defaults seguros

## 4. Segurança

### 4.1 Código

- Não expor secrets
- Validar inputs
- Sanitizar outputs
- Manter dependências seguras

### 4.2 Infraestrutura

- CORS configurado
- Rate limiting
- Autenticação/Autorização
- Backups automáticos
