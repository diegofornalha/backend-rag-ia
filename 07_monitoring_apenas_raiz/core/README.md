# Controle de Refatorações

Este módulo fornece ferramentas para controlar e monitorar o processo de refatoração, ajudando a evitar over-engineering e garantindo que as mudanças permaneçam efetivas e significativas.

## Componentes

### RefactoringLimitsChecker

Classe principal que implementa a lógica de controle de refatorações. Monitora:

- Número de iterações
- Impacto das mudanças
- Ratio de consolidação
- Retornos diminutos

### CLI

Interface de linha de comando para usar o checker:

```bash
python refactoring_cli.py --iteration 1 --removed 2 --simplified 3 --updated 1 --consolidated 1
```

Argumentos:

- `--iteration`: Número da iteração atual (obrigatório)
- `--removed`: Número de itens removidos
- `--simplified`: Número de itens simplificados
- `--updated`: Número de itens atualizados
- `--consolidated`: Número de itens consolidados
- `--project-root`: Caminho raiz do projeto (opcional)

## Configuração

O arquivo `refactoring_config.json` permite customizar os limites:

```json
{
  "max_iterations": 5,
  "min_impact_per_change": 0.2,
  "max_consolidated_ratio": 0.8,
  "diminishing_returns_threshold": 0.3
}
```

## Histórico

O sistema mantém um histórico das refatorações em `refactoring_history.json`, que pode ser usado para análise e auditoria.

## Exemplo de Uso

1. Configure os limites em `refactoring_config.json`
2. Execute o CLI após cada iteração de refatoração:

```bash
python refactoring_cli.py --iteration 1 \
    --removed 2 \
    --simplified 3 \
    --updated 1 \
    --consolidated 1
```

3. Analise o output:

```
=== Análise de Refatoração ===

Métricas da Iteração 1:
- Items Removidos: 2
- Items Simplificados: 3
- Items Atualizados: 1
- Items Consolidados: 1
- Total de Mudanças: 7

Resultado: Continuar
Motivo: Primeira iteração

Recomendações:
- Volume adequado de mudanças
- Boa distribuição entre remoção e simplificação
```

4. Use as recomendações para guiar a próxima iteração

## Integração com Complexidade

Este módulo se integra com o `ComplexityChecker` existente, complementando a análise de complexidade com métricas específicas de refatoração.

## Boas Práticas

1. Mantenha iterações pequenas e focadas
2. Equilibre remoção e simplificação
3. Evite consolidação excessiva
4. Monitore o impacto das mudanças
5. Pare quando os retornos começarem a diminuir

## Contribuindo

Para contribuir:

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Adicione testes
4. Envie um pull request

## Licença

MIT
