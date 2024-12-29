import os
import shutil
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração dos diretórios
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
BUILD_DIR = os.path.join(os.path.dirname(__file__), 'static_build')

def setup_jinja():
    """Configura o ambiente Jinja2"""
    return Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def clean_build_dir():
    """Limpa o diretório de build"""
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

def copy_static_files():
    """Copia arquivos estáticos para o diretório de build"""
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, BUILD_DIR, dirs_exist_ok=True)

def build_templates():
    """Renderiza templates para HTML estático"""
    env = setup_jinja()
    
    # Variáveis para os templates
    template_vars = {
        'health_status': {'status': 'OK'},
        'api_url': os.getenv('API_URL', 'http://localhost:8002')
    }
    
    # Lista de templates para renderizar
    templates = ['index.html']
    
    for template_name in templates:
        template = env.get_template(template_name)
        output = template.render(**template_vars)
        
        output_path = os.path.join(BUILD_DIR, template_name)
        with open(output_path, 'w') as f:
            f.write(output)

def main():
    """Função principal do build"""
    print("Iniciando build...")
    
    # Limpa e prepara diretório de build
    clean_build_dir()
    print("✓ Diretório de build limpo")
    
    # Copia arquivos estáticos
    copy_static_files()
    print("✓ Arquivos estáticos copiados")
    
    # Renderiza templates
    build_templates()
    print("✓ Templates renderizados")
    
    print("Build concluído com sucesso!")

if __name__ == '__main__':
    main() 