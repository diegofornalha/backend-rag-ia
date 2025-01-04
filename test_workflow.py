from backend_rag_ia.templates.embate_templates import EmbateTemplates
from backend_rag_ia.storage.embates_storage import EmbatesStorage
from backend_rag_ia.metrics.workflow_metrics import WorkflowMetrics
import subprocess
import os
import json

def run_git_command(command: str) -> tuple[int, str]:
    """Executa um comando git e retorna o código de saída e output"""
    print(f"Executando: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    result = (output or error).decode()
    print(f"Resultado: {result}")
    return process.returncode, result

print("1. Criando diretórios...")
os.makedirs('dados/embates', exist_ok=True)
os.makedirs('dados/backup', exist_ok=True)
os.makedirs('dados/relatorios', exist_ok=True)

print("\n2. Inicializando componentes...")
storage = EmbatesStorage('dados/embates', 'dados/backup')
metrics = WorkflowMetrics()

print("\n3. Criando embate...")
templates = EmbateTemplates()
embate = templates.create_tech_debt_embate(
    titulo="Resolução de Inconsistências do Sistema",
    descricao="""
Objetivo: Identificar e corrigir inconsistências no sistema de forma sistemática.

Áreas de Verificação:
1. Validação de Dados
   - Verificar tipos de dados
   - Validar formatos de datas
   - Confirmar campos obrigatórios

2. Integridade Referencial
   - Verificar referências entre embates
   - Validar estados e transições
   - Confirmar histórico de mudanças

3. Armazenamento
   - Verificar estrutura de diretórios
   - Validar formato dos arquivos
   - Confirmar backups

4. Métricas e Relatórios
   - Verificar coleta de métricas
   - Validar geração de relatórios
   - Confirmar integridade dos dados

Metodologia:
1. Análise sistemática de cada área
2. Documentação das inconsistências encontradas
3. Correção pontual de cada problema
4. Testes de validação
5. Documentação das correções
""",
    autor="Arquiteto",
    componente="sistema"
)

print("\nConteúdo do embate:")
print(json.dumps(embate, indent=2))

print("\n4. Salvando embate...")
embate_id = storage.save_embate(embate)
print(f"Embate criado: {embate_id}")

print("\n5. Registrando métricas...")
metrics.record_operation(embate_id, 'create')

print("\n6. Realizando commit e push...")
# Primeiro, cria/muda para a branch
branch = "fix/inconsistencias-sistema"
code, output = run_git_command(f"git checkout -b {branch}")
if code != 0:
    # Se a branch já existe, apenas muda para ela
    code, output = run_git_command(f"git checkout {branch}")
    if code != 0:
        print(f"Erro ao mudar para a branch {branch}: {output}")
        exit(1)

files_to_add = [
    'dados/embates/',
    'dados/backup/',
    'dados/relatorios/',
    'backend_rag_ia/',
    'test_workflow.py'
]

for file_path in files_to_add:
    if os.path.exists(file_path):
        print(f"\nAdicionando {file_path}...")
        code, output = run_git_command(f"git add {file_path}")
        if code != 0:
            print(f"Erro ao adicionar {file_path}: {output}")

print("\nFazendo commit...")
msg = "chore: inicia resolução sistemática de inconsistências"
code, output = run_git_command('git commit -m "' + msg + '"')
if code != 0:
    print(f"Erro ao fazer commit: {output}")
else:
    print("Commit realizado com sucesso")

    print("\nFazendo push...")
    code, output = run_git_command(f"git push -u origin {branch}")
    if code != 0:
        print(f"Erro ao fazer push: {output}")
    else:
        print("Push realizado com sucesso")

print("\nFluxo de trabalho concluído!") 