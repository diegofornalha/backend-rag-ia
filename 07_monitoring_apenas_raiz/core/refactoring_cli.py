"""CLI para controle de refatorações."""

import argparse
import logging
from pathlib import Path
from typing import Optional

from refactoring_limits_checker import RefactoringLimitsChecker, RefactoringMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def parse_args():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Controle de limites para refatorações'
    )
    
    parser.add_argument(
        '--removed',
        type=int,
        default=0,
        help='Número de itens removidos'
    )
    
    parser.add_argument(
        '--simplified',
        type=int,
        default=0,
        help='Número de itens simplificados'
    )
    
    parser.add_argument(
        '--updated',
        type=int,
        default=0,
        help='Número de itens atualizados'
    )
    
    parser.add_argument(
        '--consolidated',
        type=int,
        default=0,
        help='Número de itens consolidados'
    )
    
    parser.add_argument(
        '--iteration',
        type=int,
        required=True,
        help='Número da iteração atual'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        help='Caminho raiz do projeto'
    )
    
    return parser.parse_args()

def main():
    """Função principal do CLI."""
    args = parse_args()
    
    project_root = Path(args.project_root) if args.project_root else None
    checker = RefactoringLimitsChecker(project_root)
    
    total_changes = (
        args.removed +
        args.simplified +
        args.updated +
        args.consolidated
    )
    
    current_metrics = RefactoringMetrics(
        removed_items=args.removed,
        simplified_items=args.simplified,
        updated_items=args.updated,
        consolidated_items=args.consolidated,
        total_changes=total_changes,
        iterations=args.iteration
    )
    
    result = checker.should_continue_refactoring(current_metrics)
    
    print("\n=== Análise de Refatoração ===")
    print(f"\nMétricas da Iteração {args.iteration}:")
    print(f"- Items Removidos: {args.removed}")
    print(f"- Items Simplificados: {args.simplified}")
    print(f"- Items Atualizados: {args.updated}")
    print(f"- Items Consolidados: {args.consolidated}")
    print(f"- Total de Mudanças: {total_changes}")
    
    print(f"\nResultado: {'Continuar' if result['continue'] else 'Parar'}")
    print(f"Motivo: {result['reason']}")
    
    print("\nRecomendações:")
    for rec in checker.get_recommendations():
        print(f"- {rec}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise 