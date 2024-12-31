# Regras Principais do Projeto

## 1. Diretriz Fundamental: Consultar Antes de Criar

### 1.1 Princípio Base

- **SEMPRE** consultar recursos existentes antes de criar novos
- Evitar duplicação de funcionalidades
- Priorizar reutilização e integração
- Manter a complexidade controlada

### 1.2 Processo de Consulta

1. **Verificar Existência**:

   - Buscar em toda a base de código
   - Consultar documentação existente
   - Verificar funcionalidades similares
   - Analisar possibilidade de adaptação

2. **Antes de Criar**:

   - Justificar necessidade de novo recurso
   - Documentar tentativas de reutilização
   - Explicar por que recursos existentes não atendem
   - Propor integração com existente quando possível

3. **Se Precisar Criar**:
   - Documentar decisão e motivos
   - Garantir integração com existente
   - Manter simplicidade
   - Evitar duplicação de código

## 2. Ambiente de Desenvolvimento

- **Sistema**: macOS (ARM)
- **Stack**: Python + FastAPI
- **Padrão**: Server-side first

## 3. Regras Fundamentais

1. **Idioma**:

   - Documentação em português BR
   - Código em inglês
   - Commits em inglês

2. **Organização**:

   - Frontend em `API_frontend_flask`
   - APIs em `clusters_API`
   - Documentação em `regras_md`

3. **Proibições**:
   - ❌ Vue.js no frontend
   - ❌ Mistura server-side/client-side
   - ❌ Duplicação de código
   - ❌ Criar sem consultar existente

## 4. Documentos Relacionados

1. [Docker](./docker/REGRAS_DOCKER_VERIFICACAO.md)

   - Regras de build
   - Verificação de imagens
   - Deploy

2. [Verificação](./REGRAS_VERIFICACAO_DUPLA.md)

   - Processo de verificação
   - Documentação necessária
   - Exemplos

3. [Desenvolvimento](./desenvolvimento/PERGUNTAS_FREQUENTES.md)

   - FAQ
   - Próximos passos
   - Troubleshooting

4. [Exemplos](./exemplos/DOCSTRING_EXEMPLO.md)
   - Padrões de código
   - Documentação
   - Boas práticas

## 5. Fluxo de Trabalho

1. **Antes de Criar**:

   - Verificar duplicidade
   - Consultar documentação
   - Seguir padrões
   - **SEMPRE** buscar reutilização

2. **Antes de Remover**:

   - Verificar utilidade
   - Consultar desenvolvedor
   - Documentar motivo
   - Verificar dependências

3. **Ao Modificar**:
   - Fazer verificação dupla
   - Atualizar documentação
   - Testar mudanças
   - Manter simplicidade

## 6. Gestão de Recursos

1. **Prioridades**:

   - Reutilização > Criação
   - Simplicidade > Complexidade
   - Integração > Isolamento
   - Consulta > Ação imediata

2. **Manutenção**:
   - Documentar decisões
   - Manter registro de consultas
   - Justificar novas criações
   - Revisar periodicamente

## Hierarquia de Decisões

### 1. Boas Práticas vs. Preferências Pessoais

- Boas práticas de desenvolvimento têm prioridade sobre preferências pessoais
- Quando houver conflito, seguir a boa prática estabelecida
- Preferências pessoais podem ser aplicadas quando não conflitam com boas práticas
- Documentar decisões que divergem de preferências pessoais, explicando o motivo

### 2. Organização de Código

#### Isolamento de Recursos

1. Scripts (`scripts_apenas_raiz/`)

   - Manter scripts isolados do código principal
   - Organizar em categorias (busca, ambiente, monitoramento, etc.)
   - Facilita manutenção e evita poluição do código principal
   - Scripts de organização em pasta separada (`scripts/`)

2. Testes (`testes_apenas_raiz/`)

   - Manter testes isolados do código principal
   - Benefícios:
     - Otimização da imagem de produção (mais leve)
     - Menor tempo de build e deploy
     - Menor consumo de recursos
     - Segurança aprimorada
     - Facilita manutenção
   - Estrutura organizada:
     - `/unit` - Testes unitários
     - `/integration` - Testes de integração
     - `/monitoring` - Testes de monitoramento
     - `/fixtures` - Dados de teste
     - `/utils` - Utilitários de teste

3. SQL (`sql/`)
   - Organizar scripts SQL por função:
     - `/setup` - Configuração inicial
     - `/maintenance` - Scripts de manutenção
     - `/security` - Configurações de segurança
     - `/migrations` - Scripts de migração
   - Remover scripts obsoletos ou duplicados
   - Manter documentação atualizada

### 3. Princípios de Organização

1. Separação de Responsabilidades

   - Cada diretório tem um propósito específico
   - Evitar mistura de diferentes tipos de recursos
   - Facilita manutenção e entendimento

2. Limpeza Contínua

   - Remover arquivos obsoletos ou duplicados
   - Manter apenas recursos necessários
   - Documentar alterações significativas

3. Documentação

   - Manter documentação organizada por categoria
   - Explicar decisões e mudanças importantes
   - Incluir razões para desvios de preferências pessoais

4. Otimização para Produção
   - Priorizar eficiência e segurança
   - Remover recursos desnecessários em produção
   - Manter código limpo e organizado
