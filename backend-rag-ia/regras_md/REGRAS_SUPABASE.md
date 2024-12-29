# Regras Essenciais Supabase

## 1. Pontos Críticos de Atenção

- Sempre verificar se o `.env` está configurado antes de rodar scripts
- Nunca exceder limite de RLS (Row Level Security)
- Manter backup dos embeddings
- Verificar hash antes de cada upload para evitar duplicatas

## 2. Processo de Upload

- Sempre gerar embeddings junto com o upload
- Verificar se documento foi vinculado corretamente ao embedding
- Aguardar confirmação de sucesso antes de prosseguir
- Manter logs de falhas de upload

## 3. Buscas e Consultas

- Usar match threshold adequado nas buscas semânticas
- Implementar fallback para buscas que não retornam resultados
- Limitar número de resultados para otimizar performance
- Cachear resultados frequentes

## 4. Manutenção

- Monitorar uso de storage
- Verificar integridade dos embeddings periodicamente
- Limpar documentos órfãos (sem embedding)
- Manter índices otimizados

## 5. Segurança

- Nunca expor chaves de API
- Usar apenas conexões seguras
- Manter políticas RLS atualizadas
- Rotacionar credenciais periodicamente
