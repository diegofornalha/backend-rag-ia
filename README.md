# Sistema de Embates

Sistema para gerenciamento e controle de embates (discussões técnicas).

## Funcionalidades

### CLI

Interface de linha de comando para gerenciamento de embates:

```bash
# Criar novo embate
embates criar --tipo feature --titulo "Nova Funcionalidade" --contexto "Descrição" --autor "João"

# Adicionar argumento
embates adicionar-argumento EMBATE_ID --autor "Maria" --tipo analise --conteudo "Análise técnica..."

# Alterar estado
embates alterar-estado EMBATE_ID --novo-estado em_andamento

# Listar métricas
embates listar-metricas
```

### Armazenamento

Sistema de persistência com backup automático:

```python
from backend_rag_ia.storage.embates_storage import EmbatesStorage

# Inicializa storage
storage = EmbatesStorage('dados/embates', 'dados/backup')

# Salva embate
embate_id = storage.save_embate(embate)

# Carrega embate
embate = storage.load_embate(embate_id)

# Cria backup
backup_path = storage.create_backup()

# Restaura backup
storage.restore_backup(backup_path)
```

### Notificações

Sistema de notificações e alertas:

```python
from backend_rag_ia.notifications.notifier import (
    EmbatesNotifier, LoggingHandler, FileHandler
)

# Inicializa notificador
notifier = EmbatesNotifier()

# Adiciona handlers
notifier.add_handler(LoggingHandler())
notifier.add_handler(FileHandler('dados/notificacoes'))

# Registra mudança de estado
notifier.notify_state_change(embate_id, 'aberto', 'em_andamento')

# Define prazo
notifier.set_deadline(embate_id, deadline)

# Verifica prazos e inatividade
notifier.check_deadlines()
notifier.check_inactivity()
```

### Relatórios

Sistema de geração de relatórios:

```python
from backend_rag_ia.reports.report_generator import ReportGenerator

# Inicializa gerador
generator = ReportGenerator(metrics, 'dados/relatorios')

# Gera relatórios específicos
generator.generate_cycle_time_report()
generator.generate_state_distribution_report()
generator.generate_operations_report()
generator.generate_state_duration_report()

# Gera relatório resumido
generator.generate_summary_report()

# Gera todos os relatórios
generator.generate_all_reports()
```

## Instalação

1. Clone o repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Testes

Execute os testes com:

```bash
pytest backend_rag_ia/tests/
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nome`)
3. Commit suas mudanças (`git commit -am 'Adiciona feature'`)
4. Push para a branch (`git push origin feature/nome`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT.
