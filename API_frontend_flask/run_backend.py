import subprocess
import sys
import os
from time import sleep

def run_backend():
    # Ativa o ambiente virtual e carrega as variáveis de ambiente
    activate_cmd = "source .venv/bin/activate && source .env"
    
    # Comando para iniciar apenas o backend
    backend_cmd = f"{activate_cmd} && python3 backend_app.py"
    
    try:
        # Inicia o processo
        print("\n🚀 Iniciando servidor backend...\n")
        
        backend = subprocess.Popen(backend_cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        print("⚙️  Backend iniciado na porta 3000")
        
        print("\n✨ Servidor rodando! Pressione Ctrl+C para parar.\n")
        
        # Mantém o script rodando
        while True:
            sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando servidor...")
        # Encerra o processo
        backend.terminate()
        print("✅ Servidor encerrado com sucesso!")
        sys.exit(0)

if __name__ == "__main__":
    run_backend() 