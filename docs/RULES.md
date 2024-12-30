# RULES FOR AI

- → Separador entre instruções diferentes

                                 1. Regras Obrigatórias:

  [] → Ações obrigatórias
  [Respostas sempre em português BR]

- [Estou no ambiente Mac considerar isso]
- [Manter boas praticas de aplicação é principalmente server-side para nao se misturar com Client-Side]
- [quando eu pedir para "rodar front", quero que trabalhe com a pasta API_frontend]
- [Se preoculpe do codigo se integrar bem com o backend em suas resposabilidades devidas]
- [Cluester frontend é a unica pasta de clusters de api que fica na pasta raiz além de clusters_API]
- [Antes de criar qualquer arquivo novo, realizar uma busca completa no código para verificar se já não existe arquivo similar ou com mesma função em outra parte do projeto, evitando assim redundância e duplicidade]
- [Ao remover ou substituir referências de uma tecnologia por outra, realizar pelo menos 2 verificações completas para garantir que a remoção foi bem sucedida]

## 10. 🔍 Regras de Verificação Dupla

1. **Remoção de Referências**

   - [SEMPRE realizar no mínimo 2 verificações completas ao remover referências]
   - [SEMPRE documentar cada verificação realizada]
   - [SEMPRE usar diferentes métodos de busca (grep, find, etc)]
   - [NUNCA assumir sucesso sem segunda verificação]

2. **Processo de Verificação**

   - Primeira Verificação:

     - Busca inicial por referências
     - Remoção das referências encontradas
     - Documentação das alterações

   - Segunda Verificação:
     - Nova busca usando método diferente
     - Verificação de arquivos relacionados
     - Confirmação de que nada foi esquecido

3. **Critérios de Conclusão**

   - [✓] Duas verificações sem encontrar referências, OU
   - [✓] Certeza absoluta com evidências documentadas
   - [✓] Testes confirmando que nada quebrou
   - [✓] Documentação das verificações realizadas

4. **Documentação Necessária**

   - Data e hora de cada verificação
   - Método usado em cada verificação
   - Arquivos verificados/alterados
   - Resultado de cada verificação

5. **Exemplo de Documentação**:

   ```markdown
   ### Remoção de Referências ao Express.js (DATA)

   1. Primeira Verificação:

      - Método: grep case-insensitive
      - Arquivos encontrados: docs/RULES.md, .cursorrules
      - Alterações: Removidas referências em ambos arquivos

   2. Segunda Verificação:
      - Método: busca em requirements.txt
      - Método: verificação de diretórios
      - Resultado: Nenhuma referência encontrada

   ✅ Conclusão: Remoção completa confirmada
   ```

❗ NUNCA considerar concluído sem as duas verificações
❗ SEMPRE documentar o processo de verificação
❗ Em caso de dúvida, realizar verificação adicional

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

### Quando Reconstruir a Imagem Docker

1. Mudanças em Dependências:

   - Quando adicionar ou remover pacotes no `requirements.txt`
   - Se atualizar versões de bibliotecas
   - Ao adicionar novas dependências do sistema no Dockerfile

2. Mudanças na Estrutura do Projeto:

   - Alterações na estrutura de diretórios que afetam o PYTHONPATH
   - Mudanças nos caminhos de importação
   - Adição de novos diretórios que precisam ser copiados para o container

3. Mudanças no Dockerfile:

   - Alterações nas configurações do container
   - Mudanças nos comandos de build
   - Atualizações na imagem base

4. Mudanças em Arquivos Estáticos:

   - Adição de novos assets
   - Atualização de arquivos de configuração
   - Mudanças em arquivos que são copiados para o container

5. Mudanças de Ambiente:
   - Alterações nas variáveis de ambiente padrão
   - Mudanças nas configurações de runtime

### Comando para Reconstruir

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t fornalha/backend:latest . --push
```

### Verificação de Imagem

Para verificar se a imagem foi publicada e atualizada corretamente:

1. Verificar no Docker Hub: https://hub.docker.com/r/fornalha/backend
2. Confirmar que a tag `latest` foi atualizada
3. Verificar se os manifestos para ambas arquiteturas (amd64 e arm64) estão presentes
