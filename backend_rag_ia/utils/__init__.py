"""
Configuração de logging do sistema.
"""

import logging

# Configura o logger principal
logger = logging.getLogger('gemini')
logger.setLevel(logging.INFO)

# Configura o handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define o formato das mensagens
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Adiciona o handler ao logger
logger.addHandler(console_handler)
