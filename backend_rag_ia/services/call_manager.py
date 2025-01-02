"""
Gerenciador de chamadas sequenciais para evitar limites do Cursor.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ChamadasSequenciaisManager:
    """Gerencia e monitora chamadas sequenciais para evitar limites."""
    
    def __init__(self, 
                 limite_aviso: int = 20,
                 limite_maximo: int = 25,
                 arquivo_estado: str = "estado_chamadas.json"):
        """
        Inicializa o gerenciador.
        
        Args:
            limite_aviso: Número de chamadas para gerar aviso
            limite_maximo: Limite máximo de chamadas permitido
            arquivo_estado: Arquivo para persistir estado
        """
        self.contador = 0
        self.limite_aviso = limite_aviso
        self.limite_maximo = limite_maximo
        self.arquivo_estado = Path(arquivo_estado)
        self.ultima_chamada = None
        self.carregar_estado()
    
    def registrar_chamada(self) -> Optional[Dict]:
        """
        Registra uma nova chamada e verifica limites.
        
        Returns:
            Dict com aviso se limite próximo, None caso contrário
        """
        agora = datetime.now()
        
        # Verifica se deve resetar contador
        if self.ultima_chamada:
            diff = (agora - self.ultima_chamada).total_seconds()
            if diff > 60:  # Reset após 1 minuto de inatividade
                self.contador = 0
        
        self.contador += 1
        self.ultima_chamada = agora
        self.salvar_estado()
        
        if self.contador >= self.limite_aviso:
            return self.criar_embate_aviso()
        return None
    
    def criar_embate_aviso(self) -> Dict:
        """
        Cria um embate de aviso sobre limite de chamadas.
        
        Returns:
            Dict com informações do embate
        """
        chamadas_restantes = self.limite_maximo - self.contador
        
        return {
            "titulo": "Aviso: Limite de Chamadas Sequenciais",
            "tipo": "sistema",
            "status": "aberto",
            "contexto": f"""
                Você está próximo do limite de chamadas sequenciais:
                - Chamadas realizadas: {self.contador}
                - Limite de aviso: {self.limite_aviso}
                - Limite máximo: {self.limite_maximo}
                - Chamadas restantes: {chamadas_restantes}
                """,
            "data_inicio": datetime.now().isoformat(),
            "argumentos": [
                {
                    "autor": "sistema",
                    "tipo": "aviso",
                    "conteudo": "Recomendações:\n1. Faça uma pausa para revisar o progresso\n2. Salve o contexto atual\n3. Considere dividir a tarefa em partes menores",
                    "data": datetime.now().isoformat()
                }
            ],
            "sugestoes": [
                "pausar",      # Pausa para revisão
                "continuar",   # Continua com aviso
                "salvar",      # Salva contexto atual
                "reiniciar"    # Inicia nova sequência
            ]
        }
    
    def resetar(self) -> None:
        """Reseta o contador de chamadas."""
        self.contador = 0
        self.ultima_chamada = None
        self.salvar_estado()
    
    def salvar_estado(self) -> None:
        """Salva o estado atual em arquivo."""
        estado = {
            "contador": self.contador,
            "ultima_chamada": self.ultima_chamada.isoformat() if self.ultima_chamada else None
        }
        
        self.arquivo_estado.write_text(json.dumps(estado))
    
    def carregar_estado(self) -> None:
        """Carrega estado salvo do arquivo."""
        if not self.arquivo_estado.exists():
            return
            
        try:
            estado = json.loads(self.arquivo_estado.read_text())
            self.contador = estado.get("contador", 0)
            ultima_chamada = estado.get("ultima_chamada")
            if ultima_chamada:
                self.ultima_chamada = datetime.fromisoformat(ultima_chamada)
        except Exception:
            # Em caso de erro, mantém estado inicial
            pass 