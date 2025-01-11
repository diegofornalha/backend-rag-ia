"""
Validador de configurações do Render.
"""

import yaml
from typing import Dict, List, Any
from pathlib import Path

REQUIRED_CONFIG = {
    "databases": {
        "vector_store": {
            "backup": {
                "enabled": True,
                "schedule": "0 0 * * *",
                "retentionPeriodDays": 7,
                "alertOnFailure": True
            },
            "securityConfig": {
                "requireSSL": True,
                "sslMode": "verify-full"
            }
        },
        "cache": {
            "backup": {
                "enabled": True,
                "schedule": "0 0 * * *",
                "retentionPeriodDays": 7
            },
            "securityConfig": {
                "requireAuth": True,
                "enableTLS": True
            }
        }
    },
    "services": {
        "web": {
            "healthCheck": {
                "required": True,
                "minInterval": 10,
                "maxTimeout": 60
            },
            "autoscaling": {
                "required": True,
                "minInstances": 2
            },
            "disk": {
                "required": True,
                "backup": {
                    "required": True,
                    "schedule": "0 0 * * *",
                    "retention": 7
                }
            },
            "security": {
                "https": True,
                "hsts": True,
                "rateLimiting": True
            },
            "logging": {
                "required": True,
                "aggregation": True
            },
            "metrics": {
                "required": True,
                "alerts": True
            }
        }
    }
}

class RenderConfigValidator:
    """Validador de configurações do Render."""

    def __init__(self, config_path: str = "render.yaml"):
        """
        Inicializa o validador.

        Args:
            config_path: Caminho para o arquivo render.yaml
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.validation_errors = []

    def _load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do arquivo."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Erro ao carregar {self.config_path}: {e}")

    def validate_database_config(self, db_config: Dict[str, Any], required: Dict[str, Any]) -> List[str]:
        """Valida configurações de banco de dados."""
        errors = []
        
        # Backup
        if required.get("backup", {}).get("enabled"):
            if not db_config.get("backup", {}).get("enabled"):
                errors.append("Backup não está habilitado")
            if db_config.get("backup", {}).get("schedule") != required["backup"]["schedule"]:
                errors.append("Schedule de backup incorreto")
            if db_config.get("backup", {}).get("retentionPeriodDays") < required["backup"]["retentionPeriodDays"]:
                errors.append("Período de retenção de backup insuficiente")

        # Segurança
        if required.get("securityConfig"):
            security = db_config.get("securityConfig", {})
            required_security = required["securityConfig"]
            
            for key, value in required_security.items():
                if security.get(key) != value:
                    errors.append(f"Configuração de segurança {key} incorreta")

        return errors

    def validate_service_config(self, svc_config: Dict[str, Any], required: Dict[str, Any]) -> List[str]:
        """Valida configurações de serviço."""
        errors = []

        # Health Check
        if required["healthCheck"]["required"]:
            health = svc_config.get("healthCheck", {})
            if not health:
                errors.append("Health check não configurado")
            elif health.get("interval", 0) < required["healthCheck"]["minInterval"]:
                errors.append("Intervalo de health check muito baixo")
            elif health.get("timeout", 0) > required["healthCheck"]["maxTimeout"]:
                errors.append("Timeout de health check muito alto")

        # Autoscaling
        if required["autoscaling"]["required"]:
            auto = svc_config.get("autoscaling", {})
            if not auto:
                errors.append("Autoscaling não configurado")
            elif auto.get("min", 0) < required["autoscaling"]["minInstances"]:
                errors.append("Número mínimo de instâncias insuficiente")

        # Disco persistente
        if required["disk"]["required"]:
            disk = svc_config.get("disk", {})
            if not disk:
                errors.append("Disco persistente não configurado")
            elif required["disk"].get("backup", {}).get("required"):
                if not disk.get("backupSchedule"):
                    errors.append("Backup de disco não configurado")

        # Segurança
        if required["security"].get("https") and not svc_config.get("securityConfig", {}).get("enableHTTPS"):
            errors.append("HTTPS não habilitado")
        if required["security"].get("hsts") and not svc_config.get("securityConfig", {}).get("hsts", {}).get("enabled"):
            errors.append("HSTS não habilitado")
        if required["security"].get("rateLimiting") and not svc_config.get("securityConfig", {}).get("rateLimiting", {}).get("enabled"):
            errors.append("Rate limiting não habilitado")

        # Logging
        if required["logging"]["required"]:
            logging = svc_config.get("logging", {})
            if not logging:
                errors.append("Logging não configurado")
            elif required["logging"].get("aggregation") and not logging.get("aggregation", {}).get("enabled"):
                errors.append("Agregação de logs não habilitada")

        # Métricas
        if required["metrics"]["required"]:
            metrics = svc_config.get("metrics", {})
            if not metrics:
                errors.append("Métricas não configuradas")
            elif required["metrics"].get("alerts") and not metrics.get("alerts"):
                errors.append("Alertas de métricas não configurados")

        return errors

    def validate(self) -> List[str]:
        """Valida todas as configurações."""
        self.validation_errors = []

        # Valida bancos de dados
        for db_name, db_required in REQUIRED_CONFIG["databases"].items():
            db_config = next((db for db in self.config.get("databases", []) if db["name"] == db_name), None)
            if not db_config:
                self.validation_errors.append(f"Banco de dados {db_name} não encontrado")
            else:
                self.validation_errors.extend(self.validate_database_config(db_config, db_required))

        # Valida serviços
        for svc_type, svc_required in REQUIRED_CONFIG["services"].items():
            svc_config = next((svc for svc in self.config.get("services", []) if svc["type"] == svc_type), None)
            if not svc_config:
                self.validation_errors.append(f"Serviço do tipo {svc_type} não encontrado")
            else:
                self.validation_errors.extend(self.validate_service_config(svc_config, svc_required))

        return self.validation_errors

    def is_valid(self) -> bool:
        """Verifica se a configuração é válida."""
        return len(self.validate()) == 0

    def save_validation_state(self) -> None:
        """Salva o estado da validação."""
        validation_path = self.config_path.parent / ".render_validation"
        validation_state = {
            "timestamp": str(datetime.now()),
            "is_valid": self.is_valid(),
            "errors": self.validation_errors,
            "config_hash": hashlib.sha256(
                yaml.dump(self.config).encode()
            ).hexdigest()
        }
        
        validation_path.write_text(json.dumps(validation_state, indent=2))

    def load_validation_state(self) -> Dict[str, Any]:
        """Carrega o estado da validação."""
        validation_path = self.config_path.parent / ".render_validation"
        if not validation_path.exists():
            return {}
        
        return json.loads(validation_path.read_text())

    def has_config_changed(self) -> bool:
        """Verifica se a configuração mudou desde a última validação."""
        last_state = self.load_validation_state()
        if not last_state:
            return True
            
        current_hash = hashlib.sha256(
            yaml.dump(self.config).encode()
        ).hexdigest()
        
        return current_hash != last_state.get("config_hash") 