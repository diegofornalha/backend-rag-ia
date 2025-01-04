import pytest
from datetime import datetime, timezone, timedelta
from ..utils.date_utils import DateUtils

def test_parse_date():
    """Testa parsing de datas"""
    # Data ISO8601
    date_str = "2024-01-04T12:30:45.123456Z"
    parsed = DateUtils.parse_date(date_str)
    assert parsed is not None
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 4
    
    # Data com timezone
    date_str = "2024-01-04T12:30:45+03:00"
    parsed = DateUtils.parse_date(date_str)
    assert parsed is not None
    assert parsed.year == 2024
    assert parsed.tzinfo is not None
    
    # Data simples
    date_str = "2024-01-04"
    parsed = DateUtils.parse_date(date_str)
    assert parsed is not None
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 4
    
    # Data inválida
    assert DateUtils.parse_date("invalid") is None

def test_format_iso8601():
    """Testa formatação ISO8601"""
    # Data atual
    now = datetime.now(timezone.utc)
    formatted = DateUtils.format_iso8601(now)
    assert formatted is not None
    assert DateUtils.is_iso8601(formatted)
    
    # String ISO8601
    date_str = "2024-01-04T12:30:45Z"
    formatted = DateUtils.format_iso8601(date_str)
    assert formatted is not None
    assert DateUtils.is_iso8601(formatted)
    
    # Data sem timezone
    date = datetime(2024, 1, 4, 12, 30, 45)
    formatted = DateUtils.format_iso8601(date)
    assert formatted is not None
    assert DateUtils.is_iso8601(formatted)
    
    # Data inválida
    assert DateUtils.format_iso8601("invalid") is None

def test_is_iso8601():
    """Testa validação de formato ISO8601"""
    # Formatos válidos
    assert DateUtils.is_iso8601("2024-01-04T12:30:45Z")
    assert DateUtils.is_iso8601("2024-01-04T12:30:45.123Z")
    assert DateUtils.is_iso8601("2024-01-04T12:30:45+03:00")
    assert DateUtils.is_iso8601("2024-01-04T12:30:45.123+03:00")
    
    # Formatos inválidos
    assert not DateUtils.is_iso8601("2024-01-04")
    assert not DateUtils.is_iso8601("12:30:45")
    assert not DateUtils.is_iso8601("invalid")
    assert not DateUtils.is_iso8601("")

def test_now_iso8601():
    """Testa geração de data atual"""
    now = DateUtils.now_iso8601()
    assert DateUtils.is_iso8601(now)
    
    # Verifica se está próximo do tempo atual
    parsed = DateUtils.parse_date(now)
    assert parsed is not None
    diff = datetime.now(timezone.utc) - parsed
    assert abs(diff.total_seconds()) < 1  # Diferença menor que 1 segundo

def test_validate_date_range():
    """Testa validação de intervalo de datas"""
    # Datas válidas
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    assert DateUtils.validate_date_range(start, end)
    
    # Mesma data
    assert DateUtils.validate_date_range(start, start)
    
    # Data final menor que inicial
    assert not DateUtils.validate_date_range(end, start)
    
    # Strings ISO8601
    assert DateUtils.validate_date_range(
        "2024-01-01T00:00:00Z",
        "2024-01-02T00:00:00Z"
    )
    
    # Strings inválidas
    assert not DateUtils.validate_date_range("invalid", "2024-01-02T00:00:00Z")
    assert not DateUtils.validate_date_range("2024-01-01T00:00:00Z", "invalid")

def test_format_relative_time():
    """Testa formatação de tempo relativo"""
    now = datetime.now(timezone.utc)
    
    # Agora
    assert DateUtils.format_relative_time(now) == "agora"
    
    # Minutos atrás
    date = now - timedelta(minutes=5)
    assert DateUtils.format_relative_time(date) == "há 5 minutos"
    
    # Uma hora atrás
    date = now - timedelta(hours=1)
    assert DateUtils.format_relative_time(date) == "há 1 hora"
    
    # Horas atrás
    date = now - timedelta(hours=3)
    assert DateUtils.format_relative_time(date) == "há 3 horas"
    
    # Ontem
    date = now - timedelta(days=1)
    assert DateUtils.format_relative_time(date) == "ontem"
    
    # Dias atrás
    date = now - timedelta(days=5)
    assert DateUtils.format_relative_time(date) == "há 5 dias"
    
    # Meses atrás
    date = now - timedelta(days=60)
    assert DateUtils.format_relative_time(date) == "há 2 meses"
    
    # Anos atrás
    date = now - timedelta(days=730)
    assert DateUtils.format_relative_time(date) == "há 2 anos"
    
    # Data inválida
    assert DateUtils.format_relative_time("invalid") == "data inválida" 