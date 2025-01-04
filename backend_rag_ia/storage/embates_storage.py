import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class EmbatesStorage:
    def __init__(self, storage_dir: str, backup_dir: str = None):
        """
        Inicializa o sistema de armazenamento
        
        Args:
            storage_dir: Diretório principal para armazenamento
            backup_dir: Diretório para backups (opcional)
        """
        self.storage_dir = storage_dir
        self.backup_dir = backup_dir or os.path.join(storage_dir, 'backup')
        
        # Cria diretórios se não existirem
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        logger.info(f'Storage inicializado em: {self.storage_dir}')
        logger.info(f'Backup configurado em: {self.backup_dir}')
    
    def save_embate(self, embate: Dict) -> str:
        """
        Salva um embate no armazenamento
        
        Args:
            embate: Dicionário com dados do embate
            
        Returns:
            ID do embate salvo
        """
        embate_id = embate.get('id', str(uuid.uuid4()))
        embate['id'] = embate_id
        
        filename = f'{embate_id}.json'
        path = os.path.join(self.storage_dir, filename)
        
        with open(path, 'w') as f:
            json.dump(embate, f, indent=2)
            
        logger.info(f'Embate salvo: {embate_id}')
        return embate_id
    
    def load_embate(self, embate_id: str) -> Optional[Dict]:
        """
        Carrega um embate do armazenamento
        
        Args:
            embate_id: ID do embate
            
        Returns:
            Dicionário com dados do embate ou None se não encontrado
        """
        path = os.path.join(self.storage_dir, f'{embate_id}.json')
        
        try:
            with open(path, 'r') as f:
                embate = json.load(f)
            return embate
        except FileNotFoundError:
            logger.warning(f'Embate não encontrado: {embate_id}')
            return None
    
    def list_embates(self) -> List[str]:
        """
        Lista todos os IDs de embates armazenados
        
        Returns:
            Lista de IDs dos embates
        """
        files = os.listdir(self.storage_dir)
        return [f.replace('.json', '') for f in files if f.endswith('.json')]
    
    def create_backup(self) -> str:
        """
        Cria backup de todos os embates
        
        Returns:
            Caminho do arquivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}'
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Cria diretório de backup
        os.makedirs(backup_path, exist_ok=True)
        
        # Copia todos os arquivos
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                src = os.path.join(self.storage_dir, filename)
                dst = os.path.join(backup_path, filename)
                shutil.copy2(src, dst)
        
        # Compacta backup
        shutil.make_archive(backup_path, 'zip', backup_path)
        shutil.rmtree(backup_path)  # Remove diretório temporário
        
        logger.info(f'Backup criado: {backup_path}.zip')
        return f'{backup_path}.zip'
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restaura backup
        
        Args:
            backup_path: Caminho do arquivo de backup
            
        Returns:
            True se restaurado com sucesso
        """
        if not os.path.exists(backup_path):
            logger.error(f'Backup não encontrado: {backup_path}')
            return False
        
        # Cria diretório temporário
        temp_dir = os.path.join(self.backup_dir, 'temp_restore')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extrai backup
            shutil.unpack_archive(backup_path, temp_dir)
            
            # Limpa diretório atual
            for f in os.listdir(self.storage_dir):
                if f.endswith('.json'):
                    os.remove(os.path.join(self.storage_dir, f))
            
            # Copia arquivos do backup
            for f in os.listdir(temp_dir):
                if f.endswith('.json'):
                    src = os.path.join(temp_dir, f)
                    dst = os.path.join(self.storage_dir, f)
                    shutil.copy2(src, dst)
            
            logger.info(f'Backup restaurado: {backup_path}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao restaurar backup: {str(e)}')
            return False
            
        finally:
            shutil.rmtree(temp_dir)  # Limpa diretório temporário
    
    def delete_embate(self, embate_id: str) -> bool:
        """
        Remove um embate do armazenamento
        
        Args:
            embate_id: ID do embate
            
        Returns:
            True se removido com sucesso
        """
        path = os.path.join(self.storage_dir, f'{embate_id}.json')
        
        try:
            os.remove(path)
            logger.info(f'Embate removido: {embate_id}')
            return True
        except FileNotFoundError:
            logger.warning(f'Embate não encontrado para remoção: {embate_id}')
            return False
    
    def cleanup_old_backups(self, max_backups: int = 10) -> None:
        """
        Remove backups antigos mantendo apenas os N mais recentes
        
        Args:
            max_backups: Número máximo de backups a manter
        """
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.startswith('backup_') and f.endswith('.zip'):
                path = os.path.join(self.backup_dir, f)
                backups.append((os.path.getmtime(path), path))
        
        # Ordena por data (mais recente primeiro)
        backups.sort(reverse=True)
        
        # Remove backups excedentes
        for _, path in backups[max_backups:]:
            os.remove(path)
            logger.info(f'Backup antigo removido: {path}') 