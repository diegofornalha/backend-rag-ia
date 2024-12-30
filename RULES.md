# RULES FOR AI

- → Separador entre instruções diferentes

                                 1. Regras Obrigatórias:

  [] → Ações obrigatórias
  [Respostas sempre em português BR]

- [Estou no ambiente Mac considerar isso]
- [Projeto Flask, Jinja2 consulte a documentaçao para dividir em cluster e manter organizado, /Users/flow/Desktop/Desktop/backend/templates]
- [Manter boas praticas de aplicação é principalmente server-side para nao se misturar com Client-Side]
- [quando eu pedir para "rodar front", quero que trabalhe com a pasta API_frontend_flask]
- [Se preoculpe do codigo se integrar bem com o backend em suas resposabilidades devidas]
- [Cluester frontend é a unica pasta de clusters de api que fica na pasta raiz além de clusters_API]
- [Antes de criar qualquer arquivo novo, realizar uma busca completa no código para verificar se já não existe arquivo similar ou com mesma função em outra parte do projeto, evitando assim redundância e duplicidade]

                                       2. Observações

  () → Observações/notas adicionais
  (consulte quando necessario o package.json)

                                         3. Proibições

  X X → Expressamente proibido
  X Proibido vue no meu frontend X
  X Proibido conteúdo misto (server-side/Client-Side Vue.js) X

↓ Forçar ↓Regras de Execução (Forçar):

Se existir comando na allowlist, executar diretamente
Exemplo: pnpm → pnpm install
Exemplo: npm → npm install -g
b) Instalações:
Se houver instrução de instalação, iniciar no composer
Exemplo: /bin/bash
Exemplo: brew install node
c) Comportamento:
❌ Não perguntar permissão para continuar
❌ Não pedir confirmação para instalação
✅ Executar comandos em sequência
✅ Prosseguir automaticamente quando necessário

## FLUXO DE TRABALHO

1. Verificar regras obrigatórias
2. Manter execução contínua
3. Seguir convenções de sintaxe
4. Verificar duplicidade antes de criar arquivos

## 4. ⚠️ Regra Obrigatória de Preservação

❗ IMPORTANTE: Antes de remover qualquer funcionalidade ou endpoint:

1. **PARE IMEDIATAMENTE** se a funcionalidade tiver utilidade prática
2. **CONSULTE** o desenvolvedor sobre a remoção
3. **EXPLIQUE** claramente a utilidade da funcionalidade
4. **AGUARDE** confirmação explícita antes de prosseguir com a remoção

Esta regra existe para evitar a perda acidental de recursos úteis.

## 5. 🐳 Regras para Docker

### Sequência de Verificação de Imagens:

1. **Após Build**:

   - Verificar se o build foi concluído sem erros
   - Confirmar que todas as plataformas foram construídas (arm64/amd64)
   - Checar tamanho e layers da imagem

2. **Publicação no Docker Hub**:

   - Verificar se a imagem foi publicada em https://hub.docker.com/r/fornalha/backend
   - Confirmar que o manifesto multi-plataforma está correto
   - Validar tags e versões

3. **Monitoramento**:

   - Acompanhar status de pull/push
   - Verificar histórico de versões
   - Monitorar uso e downloads

4. **Atualização**:
   - Confirmar que a versão mais recente está disponível
   - Verificar se as tags foram atualizadas
   - Validar descrição e metadados

### ⚠️ Verificação de Prontidão para Produção:

1. **Verificação de Compatibilidade**:

   ```bash
   # Verificar arquiteturas suportadas
   docker manifest inspect fornalha/backend:latest | grep -A 3 "platform"

   # Verificar pull em diferentes ambientes
   docker pull fornalha/backend:latest
   ```

2. **Checklist de Produção**:

   - [ ] Pull bem sucedido localmente
   - [ ] Manifesto multi-plataforma válido
   - [ ] Tamanho da imagem otimizado
   - [ ] Layers corretamente cacheados
   - [ ] Sem vulnerabilidades críticas
   - [ ] Portas corretamente expostas
   - [ ] Variáveis de ambiente configuradas

3. **Validação de Ambientes**:

   - [ ] Funciona no ambiente local (Mac/ARM)
   - [ ] Compatível com GitHub Actions (Linux/AMD64)
   - [ ] Pronto para Render (Linux/AMD64)
   - [ ] Testado em todas plataformas alvo

4. **Verificação Final**:

   ```bash
   # Verificar estado da imagem
   docker inspect fornalha/backend:latest

   # Verificar histórico de camadas
   docker history fornalha/backend:latest

   # Testar execução
   docker run --rm fornalha/backend:latest python -c "print('OK')"
   ```

### Comandos de Verificação:

```bash
# Verificar manifesto
docker manifest inspect fornalha/backend:latest

# Verificar tags
docker image ls fornalha/backend

# Verificar pull
docker pull fornalha/backend:latest

# Verificar histórico
docker history fornalha/backend:latest
```

### Critérios de Validação:

✅ Imagem publicada e acessível
✅ Manifesto multi-plataforma correto
✅ Tags atualizadas
✅ Tamanho otimizado
✅ Metadata completo
✅ Pronta para produção
