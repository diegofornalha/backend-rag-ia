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

3. **Estrutura de Arquivos**:
   ```
   backend_rag_ia/
   └── regras_md/
       ├── PROJECT_RULES.md
       ├── REGRAS_API.md
       ├── REGRAS_DOCKER.md
       ├── REGRAS_RENDER.md
       └── ... (outros arquivos de regras)
   ```

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
- Seguir convenções de ferramentas similares
- Exemplos:
  - `fmt.py` → Formatador de código
  - `docker_monitor.py` → Monitoramento de build Docker
  - `prod_check.py` → Verificador de produção
  - `render_ctl.py` → Controlador do Render
  - `ssh_ctl.sh` → Controlador de SSH
  - `init.sh` → Inicializador do ambiente

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
