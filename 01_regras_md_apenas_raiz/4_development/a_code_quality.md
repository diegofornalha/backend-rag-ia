# Regras de Qualidade de Código

## 1. Princípios de Design

### 1.1 DRY (Don't Repeat Yourself)

- Evite duplicação de código
- Extraia lógicas comuns para funções reutilizáveis
- Mantenha uma única fonte de verdade

### 1.2 SOLID

- **S**ingle Responsibility: Uma classe deve ter apenas uma razão para mudar
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Subtipos devem ser substituíveis por seus tipos base
- **I**nterface Segregation: Interfaces específicas são melhores que uma geral
- **D**ependency Inversion: Dependa de abstrações, não de implementações

### 1.3 Coesão e Acoplamento

- Crie classes e métodos com responsabilidades bem definidas
- Minimize o acoplamento entre módulos
- Use injeção de dependência quando apropriado

## 2. Estratégias de Refatoração

### 2.1 Extração de Código

- Identifique padrões repetidos
- Crie funções utilitárias para código comum
- Mantenha funções pequenas e focadas

### 2.2 Herança e Composição

- Prefira composição sobre herança quando possível
- Use herança apenas para relações "é um"
- Implemente interfaces para definir contratos

### 2.3 Padrões de Design

- Use padrões estabelecidos quando apropriado
- Documente o uso de padrões
- Evite over-engineering

## 3. Processo de Revisão

### 3.1 Code Review

- Estabeleça checklist de revisão
- Use ferramentas de análise estática
- Faça revisões por pares

### 3.2 Feedback

- Colete feedback da equipe regularmente
- Implemente melhorias sugeridas
- Mantenha comunicação aberta

### 3.3 Consistência

- Siga style guides estabelecidos
- Use formatadores automáticos
- Mantenha convenções de nomenclatura
