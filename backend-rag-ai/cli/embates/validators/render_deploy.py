"""
Validador de deploy no Render.
"""

import json
import yaml
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

class RenderDeployValidator:
    """Validador de deploy no Render."""

    def __init__(self, config_path: str = "render.yaml"):
        """
        Inicializa o validador.

        Args:
            config_path: Caminho para o arquivo render.yaml
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.validation_errors = []
        self.deploy_checks = {
            "filesystem": self._check_filesystem,
            "zero_downtime": self._check_zero_downtime,
            "health_checks": self._check_health_checks,
            "dependencies": self._check_dependencies,
            "environment": self._check_environment,
            "security": self._check_security,
            "monitoring": self._check_monitoring,
            "backup": self._check_backup,
            "scaling": self._check_scaling
        }

    def _load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do arquivo."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Erro ao carregar {self.config_path}: {e}")

    def _check_filesystem(self) -> List[str]:
        """Verifica configurações do filesystem."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            errors.append("Serviço web não encontrado")
            return errors

        # Verifica disco persistente
        if not web_service.get("disk"):
            errors.append("Disco persistente não configurado - dados serão perdidos entre deploys")
        else:
            disk = web_service["disk"]
            if not disk.get("mountPath"):
                errors.append("Caminho de montagem do disco não especificado")
            if not disk.get("sizeGB"):
                errors.append("Tamanho do disco não especificado")
            if not disk.get("backupSchedule"):
                errors.append("Backup do disco não configurado")

        return errors

    def _check_zero_downtime(self) -> List[str]:
        """Verifica configurações de zero-downtime deploy."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        # Se tem disco persistente, zero-downtime deve estar desabilitado
        if web_service.get("disk") and web_service.get("zeroDowntimeDeployment", True):
            errors.append("Zero-downtime deployment deve estar desabilitado quando usando disco persistente")

        # Verifica configurações de graceful shutdown
        if not web_service.get("maxShutdownDelaySeconds"):
            errors.append("maxShutdownDelaySeconds não configurado")
        if not web_service.get("gracefulShutdownTimeout"):
            errors.append("gracefulShutdownTimeout não configurado")

        return errors

    def _check_health_checks(self) -> List[str]:
        """Verifica configurações de health check."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        # Verifica configurações obrigatórias
        if not web_service.get("healthCheckPath"):
            errors.append("Health check path não configurado")
        if not web_service.get("healthCheckInterval"):
            errors.append("Intervalo de health check não configurado")
        if not web_service.get("healthCheckTimeout"):
            errors.append("Timeout de health check não configurado")
        if not web_service.get("healthCheckRetries"):
            errors.append("Número de tentativas de health check não configurado")

        return errors

    def _check_dependencies(self) -> List[str]:
        """Verifica configurações de dependências."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        # Verifica build command
        if not web_service.get("buildCommand"):
            errors.append("Build command não configurado")
        else:
            build_cmd = web_service["buildCommand"]
            if "pip install" not in build_cmd:
                errors.append("Instalação de dependências não configurada no build command")
            if "pytest" not in build_cmd:
                errors.append("Testes não configurados no build command")

        # Verifica runtime
        if not web_service.get("pythonVersion"):
            errors.append("Versão do Python não especificada")

        return errors

    def _check_environment(self) -> List[str]:
        """Verifica configurações de ambiente."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        required_vars = {
            "ENVIRONMENT": "Variável de ambiente",
            "PYTHONPATH": "PYTHONPATH",
            "PORT": "Porta",
            "HOST": "Host",
            "WORKERS": "Número de workers",
            "LOG_LEVEL": "Nível de log"
        }

        env_vars = {var["key"]: var for var in web_service.get("envVars", [])}
        
        for key, desc in required_vars.items():
            if key not in env_vars:
                errors.append(f"{desc} não configurado")

        return errors

    def _check_security(self) -> List[str]:
        """Verifica configurações de segurança."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        security = web_service.get("securityConfig", {})
        
        # HTTPS
        if not security.get("enableHTTPS"):
            errors.append("HTTPS não habilitado")
        if not security.get("forceHTTPS"):
            errors.append("HTTPS forçado não habilitado")

        # HSTS
        hsts = security.get("hsts", {})
        if not hsts.get("enabled"):
            errors.append("HSTS não habilitado")
        if not hsts.get("maxAge"):
            errors.append("HSTS max age não configurado")

        # Rate Limiting
        rate_limit = security.get("rateLimiting", {})
        if not rate_limit.get("enabled"):
            errors.append("Rate limiting não habilitado")

        return errors

    def _check_monitoring(self) -> List[str]:
        """Verifica configurações de monitoramento."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        # Métricas
        metrics = web_service.get("metrics", {})
        if not metrics.get("enabled"):
            errors.append("Métricas não habilitadas")
        if not metrics.get("path"):
            errors.append("Path de métricas não configurado")
        if not metrics.get("alerts"):
            errors.append("Alertas de métricas não configurados")

        # Logging
        logging = web_service.get("logging", {})
        if not logging.get("driver"):
            errors.append("Driver de logging não configurado")
        if not logging.get("aggregation", {}).get("enabled"):
            errors.append("Agregação de logs não habilitada")

        return errors

    def _check_backup(self) -> List[str]:
        """Verifica configurações de backup."""
        errors = []
        
        # Verifica bancos de dados
        for db in self.config.get("databases", []):
            backup = db.get("backup", {})
            if not backup.get("enabled"):
                errors.append(f"Backup não habilitado para {db['name']}")
            if not backup.get("schedule"):
                errors.append(f"Schedule de backup não configurado para {db['name']}")
            if not backup.get("retentionPeriodDays"):
                errors.append(f"Período de retenção de backup não configurado para {db['name']}")

        # Verifica disco persistente
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        if web_service and web_service.get("disk"):
            if not web_service["disk"].get("backupSchedule"):
                errors.append("Backup do disco persistente não configurado")

        return errors

    def _check_scaling(self) -> List[str]:
        """Verifica configurações de escalabilidade."""
        errors = []
        web_service = next((svc for svc in self.config.get("services", []) if svc["type"] == "web"), None)
        
        if not web_service:
            return ["Serviço web não encontrado"]

        auto = web_service.get("autoscaling", {})
        if not auto:
            errors.append("Autoscaling não configurado")
        else:
            if auto.get("min", 0) < 2:
                errors.append("Mínimo de instâncias deve ser 2 ou mais para alta disponibilidade")
            if not auto.get("metrics"):
                errors.append("Métricas de autoscaling não configuradas")

        return errors

    def validate(self) -> List[str]:
        """Executa todas as validações."""
        self.validation_errors = []
        
        for check_name, check_func in self.deploy_checks.items():
            errors = check_func()
            if errors:
                self.validation_errors.extend([f"[{check_name}] {error}" for error in errors])

        return self.validation_errors

    def is_valid(self) -> bool:
        """Verifica se a configuração é válida."""
        return len(self.validate()) == 0

    def save_validation_state(self) -> None:
        """Salva o estado da validação."""
        validation_path = self.config_path.parent / ".render_deploy_validation"
        validation_state = {
            "timestamp": str(datetime.now()),
            "is_valid": self.is_valid(),
            "errors": self.validation_errors,
            "checks": {name: bool(not self.deploy_checks[name]()) for name in self.deploy_checks}
        }
        
        validation_path.write_text(json.dumps(validation_state, indent=2))

    def load_validation_state(self) -> Dict[str, Any]:
        """Carrega o estado da validação."""
        validation_path = self.config_path.parent / ".render_deploy_validation"
        if not validation_path.exists():
            return {}
        
        return json.loads(validation_path.read_text()) 