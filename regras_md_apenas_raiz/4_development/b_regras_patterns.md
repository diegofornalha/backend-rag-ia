# Regras de Padrões de Projeto

## 1. Padrões Criacionais

### 1.1 Factory Method

- Usar para criar objetos sem especificar a classe exata
- Implementar quando há famílias de objetos relacionados
- Facilitar extensibilidade do código
- Encapsular lógica de criação

### 1.2 Singleton

- Utilizar com cautela e apenas quando necessário
- Garantir thread-safety quando aplicável
- Implementar lazy loading
- Documentar razão do uso

### 1.3 Builder

- Separar construção de representação
- Permitir diferentes representações
- Encapsular código de construção complexo
- Facilitar criação passo a passo

## 2. Padrões Estruturais

### 2.1 Adapter

- Converter interfaces incompatíveis
- Reutilizar classes existentes
- Manter código legado compatível
- Facilitar integração de sistemas

### 2.2 Decorator

- Adicionar responsabilidades dinamicamente
- Manter princípio Open/Closed
- Criar hierarquia de decoradores
- Evitar classes muito específicas

### 2.3 Composite

- Tratar objetos individuais e composições uniformemente
- Criar estruturas em árvore
- Simplificar código cliente
- Facilitar adição de novos tipos

## 3. Padrões Comportamentais

### 3.1 Observer

- Implementar para notificações de mudanças
- Manter baixo acoplamento
- Suportar broadcast de mudanças
- Gerenciar ciclo de vida dos observers

### 3.2 Strategy

- Encapsular algoritmos intercambiáveis
- Permitir mudança de comportamento em runtime
- Eliminar condicionais complexos
- Facilitar adição de novos algoritmos

### 3.3 Command

- Encapsular requisições como objetos
- Parametrizar clientes com operações
- Suportar operações reversíveis
- Implementar filas de comandos

## 4. Boas Práticas

### 4.1 Aplicação

- Escolher padrões apropriados ao contexto
- Não forçar uso desnecessário
- Combinar padrões quando benéfico
- Documentar uso de padrões

### 4.2 Manutenção

- Refatorar código para padrões quando necessário
- Manter consistência na implementação
- Revisar uso periodicamente
- Atualizar documentação
