# Módulo de Logging e Mensagens

Este documento descreve como utilizar o módulo centralizado de logging e mensagens padronizadas da aplicação.

## Características

- Configuração centralizada
- Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formatação consistente das mensagens
- Rotação automática de arquivos de log
- Suporte a múltiplos loggers
- Tipagem estática completa
- Mensagens padronizadas para erros e sucessos
- Templates pré-definidos para diferentes tipos de operações

## Como Usar

### Logger Padrão

```python
from utils.logger import default_logger
from utils.messages import MessageTemplate, get_status_message, StatusType

# Exemplos de uso básico
default_logger.debug("Mensagem de debug")
default_logger.info("Operação concluída com sucesso")
default_logger.warning("Alerta: recurso próximo do limite")
default_logger.error("Erro ao processar requisição")
default_logger.critical("Erro crítico: sistema indisponível")

# Exemplos com mensagens padronizadas
default_logger.info(
    get_status_message(
        StatusType.SUCCESS,
        operation="backup",
        details={"files": 100}
    )
)

default_logger.error(
    MessageTemplate.DB_CONNECTION_ERROR.format(
        db_name="postgres",
        error="timeout"
    )
)
```

### Logger Personalizado

```python
from utils.logger import get_logger
from utils.messages import MessageTemplate

# Criar logger para um módulo específico
logger = get_logger(
    name="meu_modulo",
    level="DEBUG",
    log_file="logs/meu_modulo.log"
)

# Usar o logger com mensagens padronizadas
logger.info(MessageTemplate.PROCESS_START.format(process="importação"))
logger.debug("Detalhes do processamento: %s", dados)
logger.error(
    MessageTemplate.OPERATION_ERROR.format(
        operation="processamento",
        reason="dados inválidos"
    )
)
```

### Mensagens Padronizadas

O módulo `utils.messages` fornece templates pré-definidos para diferentes tipos de operações:

#### Operações Gerais

```python
from utils.messages import MessageTemplate

# Sucesso
msg = MessageTemplate.OPERATION_SUCCESS.format(operation="backup")
# "Operação concluída com sucesso: backup"

# Erro
msg = MessageTemplate.OPERATION_ERROR.format(
    operation="importação",
    reason="arquivo não encontrado"
)
# "Erro ao executar operação: importação. Motivo: arquivo não encontrado"
```

#### Banco de Dados

```python
# Conexão
msg = MessageTemplate.DB_CONNECTION_SUCCESS.format(db_name="postgres")
# "Conexão com banco de dados estabelecida: postgres"

# Erro em Query
msg = MessageTemplate.DB_QUERY_ERROR.format(
    query="SELECT * FROM users",
    error="tabela não existe"
)
# "Erro ao executar query: SELECT * FROM users. Erro: tabela não existe"
```

#### API e Autenticação

```python
# API
msg = MessageTemplate.API_REQUEST_SUCCESS.format(endpoint="/users")
# "Requisição processada com sucesso: /users"

# Autenticação
msg = MessageTemplate.AUTH_SUCCESS.format(user="john.doe")
# "Usuário john.doe autenticado com sucesso"
```

### Helper de Status

Para casos genéricos, use a função `get_status_message`:

```python
from utils.messages import get_status_message, StatusType

# Sucesso simples
msg = get_status_message(
    StatusType.SUCCESS,
    operation="sincronização"
)

# Erro com detalhes
msg = get_status_message(
    StatusType.ERROR,
    operation="processamento",
    details={"file": "data.csv", "line": 42},
    reason="formato inválido"
)
```

## Formato das Mensagens

O formato padrão das mensagens de log é:

```
2023-12-27 21:30:45,123 | INFO     | app | example.py:42 | Operação concluída com sucesso: backup
```

## Boas Práticas

1. Use os templates pré-definidos sempre que possível para manter consistência
2. Para operações comuns, prefira `get_status_message` ao invés de mensagens personalizadas
3. Mantenha as mensagens informativas mas concisas
4. Use o nível de log apropriado:
   - DEBUG: Informações detalhadas para diagnóstico
   - INFO: Confirmação de que as coisas estão funcionando
   - WARNING: Indicação de que algo inesperado aconteceu
   - ERROR: O software não pôde executar alguma função
   - CRITICAL: O programa pode não conseguir continuar rodando
5. Inclua contexto relevante nas mensagens
6. Evite logging excessivo em produção
7. Use f-strings apenas em mensagens DEBUG
8. Para mensagens com variáveis, use o estilo %-formatting ou os templates:

   ```python
   # Usando %-formatting
   logger.info("Processando usuário: %s", usuario.nome)

   # Usando template
   logger.info(MessageTemplate.AUTH_SUCCESS.format(user=usuario.nome))
   ```
