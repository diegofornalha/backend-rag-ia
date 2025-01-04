from typing import Dict, List, Optional, Set
import os
import json
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BackupValidationError(Exception):
    """Erro de validação de backup"""
    pass

class BackupValidator:
    """Validador de backups de embates"""
    
    def __init__(self, embates_dir: str, backups_dir: str):
        """
        Inicializa o validador
        
        Args:
            embates_dir: Diretório dos embates
            backups_dir: Diretório dos backups
        """
        self.embates_dir = Path(embates_dir)
        self.backups_dir = Path(backups_dir)
        
        # Cria diretório de backups se não existir
        self.backups_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calcula hash SHA256 de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Hash do arquivo
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        
        return sha256.hexdigest()
    
    def _get_backup_info(self, backup_path: Path) -> Optional[Dict]:
        """
        Obtém informações de um backup
        
        Args:
            backup_path: Caminho do backup
            
        Returns:
            Dicionário com informações ou None se inválido
        """
        try:
            info_path = backup_path / 'backup_info.json'
            if not info_path.exists():
                return None
            
            with open(info_path, 'r') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Erro ao ler informações do backup: {str(e)}")
            return None
    
    def create_backup(self, tag: str = None) -> Dict:
        """
        Cria backup dos embates
        
        Args:
            tag: Tag opcional para identificar o backup
            
        Returns:
            Informações do backup criado
        """
        try:
            # Gera nome do backup
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            if tag:
                backup_name = f"{backup_name}_{tag}"
            
            backup_path = self.backups_dir / backup_name
            backup_path.mkdir()
            
            # Copia arquivos
            files_info = []
            for file in self.embates_dir.glob("**/*.json"):
                # Calcula caminho relativo
                rel_path = file.relative_to(self.embates_dir)
                dest_path = backup_path / rel_path
                
                # Cria diretórios necessários
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copia arquivo
                shutil.copy2(file, dest_path)
                
                # Registra informações
                files_info.append({
                    'path': str(rel_path),
                    'hash': self._calculate_hash(file),
                    'size': file.stat().st_size
                })
            
            # Salva informações do backup
            backup_info = {
                'id': backup_name,
                'timestamp': timestamp,
                'tag': tag,
                'files': files_info
            }
            
            with open(backup_path / 'backup_info.json', 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return backup_info
        
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            raise BackupValidationError(f"Erro ao criar backup: {str(e)}")
    
    def validate_backup(self, backup_id: str) -> List[str]:
        """
        Valida integridade de um backup
        
        Args:
            backup_id: ID do backup
            
        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []
        
        try:
            # Localiza backup
            backup_path = self.backups_dir / backup_id
            if not backup_path.exists():
                return [f"Backup não encontrado: {backup_id}"]
            
            # Carrega informações
            backup_info = self._get_backup_info(backup_path)
            if not backup_info:
                return ["Informações do backup não encontradas ou inválidas"]
            
            # Valida cada arquivo
            for file_info in backup_info['files']:
                file_path = backup_path / file_info['path']
                
                # Verifica existência
                if not file_path.exists():
                    errors.append(f"Arquivo não encontrado: {file_info['path']}")
                    continue
                
                # Verifica tamanho
                size = file_path.stat().st_size
                if size != file_info['size']:
                    errors.append(
                        f"Tamanho incorreto para {file_info['path']}: "
                        f"esperado {file_info['size']}, encontrado {size}"
                    )
                
                # Verifica hash
                hash = self._calculate_hash(file_path)
                if hash != file_info['hash']:
                    errors.append(
                        f"Hash incorreto para {file_info['path']}: "
                        f"esperado {file_info['hash']}, encontrado {hash}"
                    )
            
            return errors
        
        except Exception as e:
            logger.error(f"Erro ao validar backup: {str(e)}")
            return [f"Erro ao validar backup: {str(e)}"]
    
    def restore_backup(
        self,
        backup_id: str,
        target_dir: Optional[str] = None
    ) -> List[str]:
        """
        Restaura um backup
        
        Args:
            backup_id: ID do backup
            target_dir: Diretório de destino (opcional)
            
        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []
        
        try:
            # Valida backup
            validation_errors = self.validate_backup(backup_id)
            if validation_errors:
                return validation_errors
            
            # Define diretório de destino
            if target_dir:
                target_path = Path(target_dir)
            else:
                target_path = self.embates_dir
            
            # Cria diretório se não existir
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Restaura arquivos
            backup_path = self.backups_dir / backup_id
            backup_info = self._get_backup_info(backup_path)
            
            for file_info in backup_info['files']:
                try:
                    source = backup_path / file_info['path']
                    target = target_path / file_info['path']
                    
                    # Cria diretórios necessários
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copia arquivo
                    shutil.copy2(source, target)
                    
                except Exception as e:
                    errors.append(
                        f"Erro ao restaurar {file_info['path']}: {str(e)}"
                    )
            
            return errors
        
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return [f"Erro ao restaurar backup: {str(e)}"]
    
    def list_backups(self) -> List[Dict]:
        """
        Lista backups disponíveis
        
        Returns:
            Lista de informações dos backups
        """
        backups = []
        
        try:
            for backup_dir in self.backups_dir.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                info = self._get_backup_info(backup_dir)
                if info:
                    backups.append(info)
            
            # Ordena por timestamp
            return sorted(
                backups,
                key=lambda x: x['timestamp'],
                reverse=True
            )
        
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []
    
    def cleanup_old_backups(
        self,
        max_backups: int = 10,
        keep_tagged: bool = True
    ) -> List[str]:
        """
        Remove backups antigos
        
        Args:
            max_backups: Número máximo de backups a manter
            keep_tagged: Se True, mantém backups com tag
            
        Returns:
            Lista de backups removidos
        """
        removed = []
        
        try:
            # Lista backups
            backups = self.list_backups()
            
            # Filtra backups a remover
            to_remove = []
            count = 0
            
            for backup in backups:
                if count >= max_backups:
                    if keep_tagged and backup.get('tag'):
                        continue
                    to_remove.append(backup['id'])
                count += 1
            
            # Remove backups
            for backup_id in to_remove:
                try:
                    backup_path = self.backups_dir / backup_id
                    shutil.rmtree(backup_path)
                    removed.append(backup_id)
                except Exception as e:
                    logger.warning(
                        f"Erro ao remover backup {backup_id}: {str(e)}"
                    )
            
            return removed
        
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")
            return [] 