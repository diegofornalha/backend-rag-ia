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
embate = templates.create_feature_embate(
    titulo="Sistema de Cache Distribuído",
    contexto="Implementar cache distribuído com Redis",
    autor="Desenvolvedor"
)

print("\nConteúdo do embate:")
print(json.dumps(embate, indent=2))

print("\n4. Salvando embate...")
embate_id = storage.save_embate(embate)
print(f"Embate criado: {embate_id}")

print("\n5. Registrando métricas...")
metrics.record_operation(embate_id, 'create')

print("\n6. Realizando commit e push...")
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
msg = "feat: implementa sistema de cache distribuído"
code, output = run_git_command('git commit -m "' + msg + '"')
if code != 0:
    print(f"Erro ao fazer commit: {output}")
else:
    print("Commit realizado com sucesso")

    print("\nFazendo push...")
    code, output = run_git_command("git push")
    if code != 0:
        print(f"Erro ao fazer push: {output}")
    else:
        print("Push realizado com sucesso")

print("\nFluxo de trabalho concluído!") 