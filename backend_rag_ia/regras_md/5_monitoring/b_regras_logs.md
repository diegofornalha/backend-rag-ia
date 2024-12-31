# Regras de Logs

## 1. Estrutura

### 1.1 Formato

- Usar JSON para logs estruturados
- Incluir timestamp em ISO 8601
- Adicionar nível de log apropriado
- Incluir identificadores de correlação

### 1.2 Campos Obrigatórios

- timestamp
- level
- message
- service_name
- trace_id
- span_id

### 1.3 Contexto

- Adicionar informações relevantes
- Incluir stack traces quando apropriado
- Manter dados sensíveis seguros
- Preservar contexto da requisição

## 2. Níveis de Log

### 2.1 DEBUG

- Informações detalhadas para debugging
- Valores de variáveis importantes
- Fluxo de execução detalhado
- Apenas em ambiente de desenvolvimento

### 2.2 INFO

- Eventos normais do sistema
- Início e fim de processos
- Mudanças de estado
- Operações bem-sucedidas

### 2.3 WARN

- Situações inesperadas mas não críticas
- Deprecation notices
- Falhas recuperáveis
- Performance degradada

### 2.4 ERROR

- Erros que afetam funcionalidade
- Exceções não tratadas
- Falhas de integração
- Problemas de segurança

## 3. Armazenamento

### 3.1 Retenção

- Definir política de retenção
- Implementar rotação de logs
- Arquivar logs antigos
- Manter compliance com regulações

### 3.2 Segurança

- Encriptar dados sensíveis
- Controlar acesso aos logs
- Auditar acessos
- Backup regular

## 4. Boas Práticas

### 4.1 Performance

- Usar logging assíncrono
- Implementar rate limiting
- Otimizar formato dos logs
- Evitar logging excessivo

### 4.2 Análise

- Implementar busca eficiente
- Facilitar correlação de eventos
- Criar dashboards de análise
- Manter ferramentas de visualização
