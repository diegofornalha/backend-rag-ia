# Sistema Multiagente

Sistema de agentes inteligentes para processamento de tarefas complexas usando o modelo Gemini.

## Estrutura

```
multiagent/
├── agents/             # Implementação dos agentes
│   ├── researcher.py   # Agente pesquisador
│   ├── analyst.py      # Agente analista
│   ├── improver.py     # Agente melhorador
│   └── synthesizer.py  # Agente sintetizador
├── core/               # Componentes principais
│   ├── config.py       # Configurações
│   ├── coordinator.py  # Coordenador dos agentes
│   ├── interfaces.py   # Interfaces base
│   ├── logging.py      # Sistema de logging
│   ├── providers.py    # Provedores LLM
│   └── tracker.py      # Sistema de tracking
└── README.md           # Este arquivo
```

## Agentes

- **ResearcherAgent**: Realiza pesquisas e coleta informações sobre um tópico
- **AnalystAgent**: Analisa informações e identifica padrões relevantes
- **ImproverAgent**: Melhora e refina o conteúdo gerado
- **SynthesizerAgent**: Sintetiza e consolida as informações

## Uso

```python
import asyncio
from multiagent.core.coordinator import AgentCoordinator
from multiagent.core.providers import GeminiProvider

async def main():
    # Configura provedor
    provider = GeminiProvider("sua-api-key")

    # Cria coordenador
    coordinator = AgentCoordinator(provider)

    # Define pipeline
    pipeline = ["researcher", "analyst", "improver", "synthesizer"]

    # Processa tarefa
    results = await coordinator.process_pipeline(
        task="Sua tarefa aqui",
        pipeline=pipeline
    )

    # Exibe resultados
    for result in results:
        print(f"\nResultado do agente '{result.agent}':")
        print(result.result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuração

O sistema pode ser configurado através do arquivo `config.py`. As principais configurações incluem:

- Configurações dos agentes (timeouts, retries, etc)
- Configurações do modelo LLM (temperatura, tokens, etc)
- Configurações de logging e tracking

## Desenvolvimento

Para executar os testes:

```bash
python -m pytest tests/multiagent/ -v
```

Para executar o exemplo:

```bash
python scripts/run_multiagent_example.py
```

## Requisitos

- Python 3.8+
- google-generativeai
- pytest (para testes)
- pytest-asyncio (para testes assíncronos)

## Licença

MIT
