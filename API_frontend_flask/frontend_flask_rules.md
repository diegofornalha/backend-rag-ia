# Características de Aplicações Server-Side

## 1. Processamento no Servidor

- Lógica de negócio
- Consultas ao banco de dados
- Formatação de dados
- Renderização de templates

## 2. Vantagens

- Melhor para SEO (otimização para buscadores)
- Menor processamento no dispositivo do usuário
- Mais seguro (lógica sensível fica no servidor)

Jinja2: Renderização estática e estrutura base

## Documentação de cada API

/Users/flow/Desktop/Desktop/backend/static/api-doc

Atualize os arquivos de documentação da API sempre que houver uma alteração na API.

## Estrutura do Projeto

### Organização

- Organizado em clusters (módulos) seguindo boas práticas
- Separação clara entre backend e frontend
- Utiliza templates Jinja2 para renderização server-side

### Principais Componentes

- `/templates`: Arquivos de template Jinja2
- `/static`: Arquivos estáticos (CSS, JS, imagens)
- `/api`: Endpoints da API
- `/models`: Modelos de dados
- `/services`: Lógica de negócios
- `/utils`: Utilitários e helpers
- `/config`: Configurações do projeto

### Tecnologias Principais

- Flask 2.3.3 como framework principal
- Jinja2 3.1.2 para templates
- Flask-CORS para gerenciamento de CORS
- Gunicorn como servidor WSGI

### Características Específicas

- Foco em server-side rendering
- Sem uso de Vue.js (conforme regras)
- Separação clara entre responsabilidades client-side e server-side
- Estrutura preparada para escalabilidade

### Ambiente

- Desenvolvido para ambiente Mac
- Usa Python com Flask
- Gerenciamento de dependências via pip/requirements.txt

> O projeto segue uma arquitetura limpa e organizada, com clara separação de responsabilidades e foco em desenvolvimento server-side, seguindo as melhores práticas de desenvolvimento web com Flask.

### Logs e Endpoints

```log
# Logs de Inicialização
🚀 Iniciando API Frontend Flask...
✅ API Frontend Flask iniciada - Versão 1.0.0
📝 Documentação: http://localhost:1000/docs

# Endpoints Disponíveis
- Aplicação: http://127.0.0.1:1000
- Documentação: http://localhost:1000/docs

# Informações do Debugger
- Debug mode: on
- Debugger PIN: [gerado automaticamente]
- Hot-reload: ativado
```

### Observações de Desenvolvimento

- Servidor de desenvolvimento não deve ser usado em produção
- Debugger ativo para desenvolvimento
- Auto-reload ativado para alterações em arquivos
- PIN do debugger gerado a cada execução

### Variáveis de Ambiente

```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
```

### Estrutura de Diretórios

```
/templates    → Templates Jinja2
/static       → Arquivos estáticos (CSS, JS, imagens)
/api          → Endpoints da API
```

### Regras de Desenvolvimento

1. Server-Side First

   - Priorizar renderização server-side
   - Usar Jinja2 para templates
   - Manter lógica no backend

2. Organização de Assets

   - CSS em /static/css
   - JS em /static/js
   - Imagens em /static/images

3. Boas Práticas

   - Separar responsabilidades
   - Manter templates organizados
   - Seguir padrões Flask/Jinja2

4. Cache e Performance
   - Usar cache de templates
   - Minificar assets estáticos
   - Otimizar carregamento de recursos

### Arquivo .env

Criar arquivo `.env` na raiz do projeto:

```env
# Configurações do Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Configurações do Servidor
HOST=0.0.0.0
PORT=1000
DEBUG=True

# Configurações da Aplicação
APP_NAME="Frontend Flask API"
APP_VERSION="1.0.0"
SECRET_KEY="sua-chave-secreta-aqui"

# Configurações de Template
TEMPLATE_FOLDER="templates"
STATIC_FOLDER="static"
STATIC_URL_PATH="/static"

# Configurações de Documentação
SWAGGER_URL="/docs"
API_URL="/static/swagger.json"
```

Para carregar as variáveis de ambiente:

```bash
source .env
```
