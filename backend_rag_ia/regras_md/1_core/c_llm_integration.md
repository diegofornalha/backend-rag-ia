# Regras de Integração com LLMs

## 1. Modelo Principal

### 1.1 Gemini

- Use Gemini como LLM principal do sistema
- Configure a API key via variáveis de ambiente
- Mantenha versão mais recente e estável

### 1.2 Configuração

- Use modelo 'gemini-pro' para processamento de texto
- Configure timeouts apropriados
- Implemente rate limiting adequado

### 1.3 Manutenção

- Monitore uso e custos
- Mantenha logs de chamadas
- Atualize conforme novas versões

## 2. Processamento

### 2.1 Prompts

- Mantenha templates de prompts organizados
- Use formatação consistente
- Documente estrutura esperada de respostas

### 2.2 Respostas

- Implemente parsing robusto de JSON
- Trate erros adequadamente
- Valide estrutura das respostas

### 2.3 Cache

- Implemente cache para respostas frequentes
- Use TTL apropriado
- Mantenha estratégia de invalidação

## 3. Resiliência

### 3.1 Error Handling

- Implemente retry com backoff
- Trate diferentes tipos de erros
- Forneça fallbacks apropriados

### 3.2 Monitoramento

- Monitore latência das chamadas
- Acompanhe taxa de sucesso
- Alerte sobre problemas

### 3.3 Otimização

- Agrupe chamadas quando possível
- Otimize tamanho dos prompts
- Monitore e ajuste uso de tokens
