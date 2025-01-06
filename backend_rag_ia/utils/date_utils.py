from datetime import datetime, timezone
from typing import Optional, Union
import re


class DateUtils:
    """Utilitários para manipulação de datas"""

    # Formatos de data suportados
    DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]

    # Formatos de data/hora suportados
    DATETIME_FORMATS = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Tenta converter uma string em data usando vários formatos

        Args:
            date_str: String contendo a data

        Returns:
            Objeto datetime ou None se não conseguir converter
        """
        # Remove espaços extras
        date_str = date_str.strip()

        # Tenta formatos de data/hora
        for fmt in DateUtils.DATETIME_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Tenta formatos de data
        for fmt in DateUtils.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def format_iso8601(date: Union[datetime, str]) -> Optional[str]:
        """
        Formata uma data no padrão ISO8601

        Args:
            date: Data a ser formatada (datetime ou string)

        Returns:
            String no formato ISO8601 ou None se não conseguir formatar
        """
        try:
            # Se for string, tenta converter
            if isinstance(date, str):
                parsed = DateUtils.parse_date(date)
                if not parsed:
                    return None
                date = parsed

            # Garante que tem timezone
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)

            return date.isoformat()

        except Exception:
            return None

    @staticmethod
    def is_iso8601(date_str: str) -> bool:
        """
        Verifica se uma string está no formato ISO8601

        Args:
            date_str: String a ser verificada

        Returns:
            True se estiver no formato ISO8601, False caso contrário
        """
        iso8601_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?" r"(Z|[+-]\d{2}:?\d{2})?$"
        return bool(re.match(iso8601_pattern, date_str))

    @staticmethod
    def now_iso8601() -> str:
        """
        Retorna a data/hora atual no formato ISO8601

        Returns:
            String no formato ISO8601
        """
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def validate_date_range(start: Union[datetime, str], end: Union[datetime, str]) -> bool:
        """
        Valida se um intervalo de datas é válido (início <= fim)

        Args:
            start: Data inicial
            end: Data final

        Returns:
            True se o intervalo é válido, False caso contrário
        """
        try:
            # Converte strings se necessário
            if isinstance(start, str):
                start = DateUtils.parse_date(start)
                if not start:
                    return False

            if isinstance(end, str):
                end = DateUtils.parse_date(end)
                if not end:
                    return False

            # Garante que tem timezone
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)

            return start <= end

        except Exception:
            return False

    @staticmethod
    def format_relative_time(date: Union[datetime, str]) -> str:
        """
        Formata uma data em tempo relativo (ex: "há 2 dias")

        Args:
            date: Data a ser formatada

        Returns:
            String com tempo relativo
        """
        try:
            # Converte string se necessário
            if isinstance(date, str):
                parsed = DateUtils.parse_date(date)
                if not parsed:
                    return "data inválida"
                date = parsed

            # Garante que tem timezone
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            diff = now - date

            # Formatação
            if diff.days == 0:
                if diff.seconds < 60:
                    return "agora"
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
                else:
                    hours = diff.seconds // 3600
                    return f"há {hours} hora{'s' if hours > 1 else ''}"
            elif diff.days == 1:
                return "ontem"
            elif diff.days < 30:
                return f"há {diff.days} dia{'s' if diff.days > 1 else ''}"
            elif diff.days < 365:
                months = diff.days // 30
                return f"há {months} mês{'es' if months > 1 else ''}"
            else:
                years = diff.days // 365
                return f"há {years} ano{'s' if years > 1 else ''}"

        except Exception:
            return "data inválida"
