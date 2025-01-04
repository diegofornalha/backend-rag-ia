import click
import json
import os
from datetime import datetime
from typing import Dict, Optional

from ..templates.embate_templates import EmbateTemplates
from ..validators.workflow_validator import WorkflowValidator
from ..metrics.workflow_metrics import WorkflowMetrics

@click.group()
def cli():
    """CLI para gerenciamento de embates"""
    pass

@cli.command()
@click.option('--tipo', type=click.Choice(['feature', 'bug', 'processo', 'tech_debt']), required=True)
@click.option('--titulo', required=True)
@click.option('--contexto', required=True)
@click.option('--autor', required=True)
@click.option('--severidade', type=click.Choice(['baixa', 'média', 'alta']), default='média')
@click.option('--area', help='Área do processo (apenas para tipo processo)')
@click.option('--componente', help='Componente afetado (apenas para tech_debt)')
def criar(tipo: str, titulo: str, contexto: str, autor: str, 
          severidade: str, area: Optional[str], componente: Optional[str]):
    """Cria novo embate"""
    templates = EmbateTemplates()
    
    if tipo == 'feature':
        embate = templates.create_feature_embate(titulo, contexto, autor)
    elif tipo == 'bug':
        embate = templates.create_bug_embate(titulo, contexto, autor, severidade)
    elif tipo == 'processo':
        if not area:
            raise click.BadParameter('Área é obrigatória para embates de processo')
        embate = templates.create_process_embate(titulo, contexto, autor, area)
    elif tipo == 'tech_debt':
        if not componente:
            raise click.BadParameter('Componente é obrigatório para embates de tech_debt')
        embate = templates.create_tech_debt_embate(titulo, contexto, autor, componente)
    
    # Valida embate
    validator = WorkflowValidator()
    validation = validator.validate_embate(embate)
    
    if any(validation.values()):
        click.echo('Erros de validação encontrados:')
        for key, errors in validation.items():
            if errors:
                click.echo(f'{key}: {errors}')
        return
    
    # Salva embate
    os.makedirs('dados/embates', exist_ok=True)
    filename = f'dados/embates/embate_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{tipo}.json'
    
    with open(filename, 'w') as f:
        json.dump(embate, f, indent=2)
    
    click.echo(f'Embate criado com sucesso: {filename}')

@cli.command()
@click.argument('embate_id')
@click.option('--autor', required=True)
@click.option('--tipo', type=click.Choice(['analise', 'solucao', 'implementacao', 'validacao']), required=True)
@click.option('--conteudo', required=True)
def adicionar_argumento(embate_id: str, autor: str, tipo: str, conteudo: str):
    """Adiciona novo argumento a um embate existente"""
    # Carrega embate
    try:
        with open(f'dados/embates/{embate_id}.json', 'r') as f:
            embate = json.load(f)
    except FileNotFoundError:
        click.echo(f'Embate não encontrado: {embate_id}')
        return
    
    # Adiciona argumento
    templates = EmbateTemplates()
    embate = templates.add_argument(embate, autor, tipo, conteudo)
    
    # Valida
    validator = WorkflowValidator()
    validation = validator.validate_embate(embate)
    
    if any(validation.values()):
        click.echo('Erros de validação encontrados:')
        for key, errors in validation.items():
            if errors:
                click.echo(f'{key}: {errors}')
        return
    
    # Salva
    with open(f'dados/embates/{embate_id}.json', 'w') as f:
        json.dump(embate, f, indent=2)
    
    click.echo('Argumento adicionado com sucesso')

@cli.command()
@click.argument('embate_id')
@click.option('--novo_estado', type=click.Choice(['em_andamento', 'bloqueado', 'fechado']), required=True)
def alterar_estado(embate_id: str, novo_estado: str):
    """Altera estado de um embate"""
    # Carrega embate
    try:
        with open(f'dados/embates/{embate_id}.json', 'r') as f:
            embate = json.load(f)
    except FileNotFoundError:
        click.echo(f'Embate não encontrado: {embate_id}')
        return
    
    # Valida transição
    validator = WorkflowValidator()
    error = validator.validate_state_transition(embate['status'], novo_estado)
    
    if error:
        click.echo(f'Erro na transição de estado: {error}')
        return
    
    # Atualiza estado
    embate['status'] = novo_estado
    
    # Registra métrica
    metrics = WorkflowMetrics()
    metrics.record_state_change(embate_id, embate['status'], novo_estado)
    
    # Salva
    with open(f'dados/embates/{embate_id}.json', 'w') as f:
        json.dump(embate, f, indent=2)
    
    click.echo(f'Estado alterado para: {novo_estado}')

@cli.command()
def listar_metricas():
    """Lista métricas do sistema"""
    metrics = WorkflowMetrics()
    stats = metrics.get_statistics()
    
    click.echo('\nEstatísticas do Sistema:')
    click.echo(f'Total de Embates: {stats["total_embates"]}')
    click.echo(f'Total de Mudanças de Estado: {stats["state_changes"]}')
    
    if stats['avg_cycle_time']:
        avg_days = stats['avg_cycle_time'] / 86400  # converte segundos para dias
        click.echo(f'Tempo Médio de Ciclo: {avg_days:.2f} dias')
    
    click.echo('\nDistribuição de Estados:')
    for state, count in stats['state_distribution'].items():
        click.echo(f'{state}: {count}')
    
    click.echo('\nOperações:')
    for op, count in stats['operations'].items():
        click.echo(f'{op}: {count}')

if __name__ == '__main__':
    cli() 