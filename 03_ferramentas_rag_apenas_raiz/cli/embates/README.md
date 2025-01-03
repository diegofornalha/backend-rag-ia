# Ferramenta de Embates

## Estrutura

A ferramenta de embates está organizada da seguinte forma:

```
03_ferramentas_rag_apenas_raiz/cli/embates/
├── commands/       # Comandos CLI para interação com embates
├── handlers/       # Handlers que processam os comandos
└── utils/          # Utilitários específicos para CLI
```

## Responsabilidades

1. **Interface com Usuário**:

   - Comandos CLI para criar, listar e gerenciar embates
   - Formatação e apresentação dos dados
   - Interação com usuário

2. **Integração com Core**:
   - Usa models do core para estrutura de dados
   - Usa services do core para lógica de negócio
   - Usa API endpoints para comunicação

## Componentes do Core Utilizados

- `backend_rag_ia/models/embates.py`: Modelos de dados
- `backend_rag_ia/services/embates.py`: Lógica de negócio
- `backend_rag_ia/api/routes/embates.py`: Endpoints da API

## Desenvolvimento

1. Novos comandos devem ser adicionados em `commands/`
2. Lógica de processamento em `handlers/`
3. Funções auxiliares em `utils/`
4. Toda lógica de negócio deve permanecer no core

## Testes

Os testes da ferramenta estão em:

- `00_testes_apenas_raiz/core/cli/test_embates_cli.py`
- `00_testes_apenas_raiz/integration/test_embates_integration.py`
