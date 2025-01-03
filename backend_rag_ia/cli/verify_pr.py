import click
from ..tools.verify_render_pr import RenderPRValidator

@click.command()
@click.option('--strict', is_flag=True, help='Falha se houver warnings')
@click.option('--check-health', is_flag=True, help='Valida endpoint de health check')
def verify_pr(strict: bool, check_health: bool):
    """Valida configurações de PR e ambiente Render"""
    validator = RenderPRValidator()
    result = validator.run_validation()
    
    # Exibe resultados
    if result.errors:
        click.secho("\n🔴 Erros encontrados:", fg="red")
        for error in result.errors:
            click.secho(error, fg="red")
            
    if result.warnings:
        click.secho("\n🟡 Avisos:", fg="yellow")
        for warning in result.warnings:
            click.secho(warning, fg="yellow")
            
    if result.suggestions:
        click.secho("\n💭 Sugestões:", fg="blue")
        for suggestion in result.suggestions:
            click.secho(suggestion, fg="blue")
            
    # Status final
    if result.is_valid and (not strict or not result.warnings):
        click.secho("\n✅ Validação concluída com sucesso!", fg="green")
        exit(0)
    else:
        click.secho("\n❌ Falha na validação", fg="red")
        exit(1)

if __name__ == "__main__":
    verify_pr() 