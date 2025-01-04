import pytest
import os
import shutil
from datetime import datetime, timedelta
import json
import pandas as pd

from ..cli.embates_cli import cli
from ..storage.embates_storage import EmbatesStorage
from ..notifications.notifier import (
    EmbatesNotifier, LoggingHandler, FileHandler, CallbackHandler
)
from ..reports.report_generator import ReportGenerator
from ..metrics.workflow_metrics import WorkflowMetrics

@pytest.fixture
def storage():
    """Fixture para storage"""
    storage_dir = 'test_storage'
    backup_dir = 'test_backup'
    
    # Limpa diretórios de teste
    for d in [storage_dir, backup_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
    
    storage = EmbatesStorage(storage_dir, backup_dir)
    yield storage
    
    # Cleanup
    for d in [storage_dir, backup_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

@pytest.fixture
def notifier():
    """Fixture para notifier"""
    return EmbatesNotifier()

@pytest.fixture
def metrics():
    """Fixture para metrics"""
    return WorkflowMetrics()

@pytest.fixture
def report_generator(metrics):
    """Fixture para report generator"""
    output_dir = 'test_reports'
    
    # Limpa diretório de teste
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    generator = ReportGenerator(metrics, output_dir)
    yield generator
    
    # Cleanup
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

def test_storage_save_load(storage):
    """Testa salvamento e carregamento de embates"""
    embate = {
        'titulo': 'Test Embate',
        'tipo': 'feature',
        'status': 'aberto'
    }
    
    # Salva
    embate_id = storage.save_embate(embate)
    assert embate_id is not None
    
    # Carrega
    loaded = storage.load_embate(embate_id)
    assert loaded is not None
    assert loaded['titulo'] == embate['titulo']
    assert loaded['tipo'] == embate['tipo']
    
def test_storage_backup(storage):
    """Testa backup e restauração"""
    # Cria alguns embates
    embates = [
        {'titulo': f'Test {i}', 'tipo': 'feature', 'status': 'aberto'}
        for i in range(3)
    ]
    
    for embate in embates:
        storage.save_embate(embate)
    
    # Cria backup
    backup_path = storage.create_backup()
    assert os.path.exists(backup_path)
    
    # Limpa storage
    for embate_id in storage.list_embates():
        storage.delete_embate(embate_id)
    
    # Restaura backup
    assert storage.restore_backup(backup_path)
    
    # Verifica restauração
    restored = storage.list_embates()
    assert len(restored) == len(embates)

def test_notifier_handlers(notifier):
    """Testa handlers de notificação"""
    # Prepara handlers
    log_handler = LoggingHandler()
    file_handler = FileHandler('test_notifications')
    callback_handler = CallbackHandler()
    
    # Adiciona handlers
    notifier.add_handler(log_handler)
    notifier.add_handler(file_handler)
    notifier.add_handler(callback_handler)
    
    # Registra callbacks
    callback_called = False
    def state_change_callback(embate_id, old_state, new_state):
        nonlocal callback_called
        callback_called = True
    
    callback_handler.add_state_change_callback(state_change_callback)
    
    # Testa notificação
    notifier.notify_state_change('test_embate', 'aberto', 'em_andamento')
    assert callback_called
    
    # Cleanup
    if os.path.exists('test_notifications'):
        shutil.rmtree('test_notifications')

def test_notifier_deadlines(notifier):
    """Testa lembretes de prazo"""
    # Configura prazo
    embate_id = 'test_embate'
    deadline = datetime.now() + timedelta(hours=23)  # Prazo em menos de 1 dia
    notifier.set_deadline(embate_id, deadline)
    
    # Adiciona handler para teste
    deadlines_checked = []
    class TestHandler:
        def handle_deadline_reminder(self, embate_id, deadline):
            deadlines_checked.append(embate_id)
    
    notifier.add_handler(TestHandler())
    
    # Verifica prazos
    notifier.check_deadlines()
    assert embate_id in deadlines_checked

def test_report_generation(report_generator, metrics):
    """Testa geração de relatórios"""
    # Registra algumas métricas
    embate_id = 'test_embate'
    metrics.record_state_change(embate_id, 'aberto', 'em_andamento')
    metrics.record_state_change(embate_id, 'em_andamento', 'fechado')
    metrics.record_operation(embate_id, 'create')
    
    # Gera relatórios
    cycle_time_df = report_generator.generate_cycle_time_report()
    assert not cycle_time_df.empty
    assert os.path.exists(os.path.join(report_generator.output_dir, 'cycle_time_report.csv'))
    
    state_dist_df = report_generator.generate_state_distribution_report()
    assert not state_dist_df.empty
    assert os.path.exists(os.path.join(report_generator.output_dir, 'state_distribution_report.csv'))
    
    summary = report_generator.generate_summary_report()
    assert summary['total_embates'] >= 1
    assert os.path.exists(os.path.join(report_generator.output_dir, 'summary_report.json'))

def test_cli_commands(storage):
    """Testa comandos da CLI"""
    from click.testing import CliRunner
    runner = CliRunner()
    
    # Testa criação de embate
    result = runner.invoke(cli, [
        'criar',
        '--tipo', 'feature',
        '--titulo', 'Test Feature',
        '--contexto', 'Test Context',
        '--autor', 'test_user'
    ])
    assert result.exit_code == 0
    assert 'Embate criado com sucesso' in result.output
    
    # Testa listagem de métricas
    result = runner.invoke(cli, ['listar_metricas'])
    assert result.exit_code == 0
    assert 'Estatísticas do Sistema' in result.output

def test_integration(storage, notifier, metrics, report_generator):
    """Testa integração entre os componentes"""
    # Cria embate via storage
    embate = {
        'titulo': 'Integration Test',
        'tipo': 'feature',
        'status': 'aberto'
    }
    embate_id = storage.save_embate(embate)
    
    # Registra mudança de estado via notifier
    notifier.notify_state_change(embate_id, 'aberto', 'em_andamento')
    
    # Verifica métricas
    stats = metrics.get_statistics()
    assert stats['total_embates'] >= 1
    assert stats['state_changes'] >= 1
    
    # Gera relatórios
    summary = report_generator.generate_summary_report()
    assert summary['total_embates'] >= 1
    assert summary['total_state_changes'] >= 1 