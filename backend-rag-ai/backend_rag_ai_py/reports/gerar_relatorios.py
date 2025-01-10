from backend_rag_ai_py.reports.report_generator import ReportGenerator
from backend_rag_ai_py.metrics.workflow_metrics import WorkflowMetrics
from datetime import datetime, timedelta

# Simula alguns dados para demonstração
metrics = WorkflowMetrics()

# Registra algumas mudanças de estado
embate_id = 'embate_20250104_123648_feature'
metrics.record_state_change(embate_id, 'aberto', 'em_andamento')
metrics.record_operation(embate_id, 'create')

# Simula algumas durações
metrics.state_changes[embate_id] = [
    {'from': 'aberto', 'to': 'em_andamento', 'timestamp': datetime.now() - timedelta(days=2)},
    {'from': 'em_andamento', 'to': 'fechado', 'timestamp': datetime.now()}
]

# Gera relatórios
generator = ReportGenerator(metrics, 'dados/relatorios')
generator.generate_all_reports()

print("Relatórios gerados em dados/relatorios/") 