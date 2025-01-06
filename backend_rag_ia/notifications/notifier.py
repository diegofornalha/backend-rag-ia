import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)


class NotificationHandler:
    """Interface base para handlers de notificação"""

    def handle_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        """Processa mudança de estado"""
        pass

    def handle_deadline_reminder(self, embate_id: str, deadline: datetime) -> None:
        """Processa lembrete de prazo"""
        pass

    def handle_inactivity_alert(self, embate_id: str, last_update: datetime) -> None:
        """Processa alerta de inatividade"""
        pass


class LoggingHandler(NotificationHandler):
    """Handler que registra notificações no log"""

    def handle_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        logger.info(f"Estado do embate {embate_id} alterado de {old_state} para {new_state}")

    def handle_deadline_reminder(self, embate_id: str, deadline: datetime) -> None:
        logger.info(f"Lembrete de prazo para embate {embate_id}: {deadline}")

    def handle_inactivity_alert(self, embate_id: str, last_update: datetime) -> None:
        logger.warning(
            f"Alerta de inatividade para embate {embate_id}. " f"Última atualização: {last_update}"
        )


class FileHandler(NotificationHandler):
    """Handler que salva notificações em arquivo"""

    def __init__(self, notifications_dir: str):
        self.notifications_dir = notifications_dir
        os.makedirs(notifications_dir, exist_ok=True)

    def _save_notification(self, notification: Dict) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notification_{timestamp}.json"
        path = os.path.join(self.notifications_dir, filename)

        with open(path, "w") as f:
            json.dump(notification, f, indent=2)

    def handle_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        self._save_notification(
            {
                "type": "state_change",
                "embate_id": embate_id,
                "old_state": old_state,
                "new_state": new_state,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def handle_deadline_reminder(self, embate_id: str, deadline: datetime) -> None:
        self._save_notification(
            {
                "type": "deadline_reminder",
                "embate_id": embate_id,
                "deadline": deadline.isoformat(),
                "timestamp": datetime.now().isoformat(),
            }
        )

    def handle_inactivity_alert(self, embate_id: str, last_update: datetime) -> None:
        self._save_notification(
            {
                "type": "inactivity_alert",
                "embate_id": embate_id,
                "last_update": last_update.isoformat(),
                "timestamp": datetime.now().isoformat(),
            }
        )


class CallbackHandler(NotificationHandler):
    """Handler que executa callbacks para notificações"""

    def __init__(self):
        self.state_change_callbacks: List[Callable] = []
        self.deadline_callbacks: List[Callable] = []
        self.inactivity_callbacks: List[Callable] = []

    def add_state_change_callback(self, callback: Callable) -> None:
        self.state_change_callbacks.append(callback)

    def add_deadline_callback(self, callback: Callable) -> None:
        self.deadline_callbacks.append(callback)

    def add_inactivity_callback(self, callback: Callable) -> None:
        self.inactivity_callbacks.append(callback)

    def handle_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        for callback in self.state_change_callbacks:
            try:
                callback(embate_id, old_state, new_state)
            except Exception as e:
                logger.error(f"Erro no callback de mudança de estado: {str(e)}")

    def handle_deadline_reminder(self, embate_id: str, deadline: datetime) -> None:
        for callback in self.deadline_callbacks:
            try:
                callback(embate_id, deadline)
            except Exception as e:
                logger.error(f"Erro no callback de prazo: {str(e)}")

    def handle_inactivity_alert(self, embate_id: str, last_update: datetime) -> None:
        for callback in self.inactivity_callbacks:
            try:
                callback(embate_id, last_update)
            except Exception as e:
                logger.error(f"Erro no callback de inatividade: {str(e)}")


class EmbatesNotifier:
    """Sistema central de notificações"""

    def __init__(self):
        self.handlers: List[NotificationHandler] = []
        self.deadlines: Dict[str, datetime] = {}
        self.last_updates: Dict[str, datetime] = {}

    def add_handler(self, handler: NotificationHandler) -> None:
        """Adiciona um handler de notificação"""
        self.handlers.append(handler)

    def notify_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        """Notifica mudança de estado"""
        for handler in self.handlers:
            try:
                handler.handle_state_change(embate_id, old_state, new_state)
            except Exception as e:
                logger.error(f"Erro ao notificar mudança de estado: {str(e)}")

        # Atualiza último update
        self.last_updates[embate_id] = datetime.now()

    def set_deadline(self, embate_id: str, deadline: datetime) -> None:
        """Define prazo para um embate"""
        self.deadlines[embate_id] = deadline

    def check_deadlines(self) -> None:
        """Verifica prazos e envia lembretes"""
        now = datetime.now()

        for embate_id, deadline in self.deadlines.items():
            # Envia lembrete 1 dia antes
            if now + timedelta(days=1) >= deadline:
                for handler in self.handlers:
                    try:
                        handler.handle_deadline_reminder(embate_id, deadline)
                    except Exception as e:
                        logger.error(f"Erro ao enviar lembrete de prazo: {str(e)}")

    def check_inactivity(self, max_days: int = 7) -> None:
        """Verifica inatividade e envia alertas"""
        now = datetime.now()

        for embate_id, last_update in self.last_updates.items():
            if now - last_update > timedelta(days=max_days):
                for handler in self.handlers:
                    try:
                        handler.handle_inactivity_alert(embate_id, last_update)
                    except Exception as e:
                        logger.error(f"Erro ao enviar alerta de inatividade: {str(e)}")

    def clear(self) -> None:
        """Limpa dados do notificador"""
        self.handlers.clear()
        self.deadlines.clear()
        self.last_updates.clear()
