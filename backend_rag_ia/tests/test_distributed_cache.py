import pytest
import redis
from unittest.mock import Mock, patch
from datetime import datetime
from ..cache.distributed_cache import DistributedCache
from ..config.redis_config import RedisConfig

@pytest.fixture
def mock_redis():
    """Mock do cliente Redis"""
    with patch('redis.from_url') as mock:
        client = Mock()
        mock.return_value = client
        yield client

@pytest.fixture
def cache(mock_redis):
    """Fixture com instância do cache"""
    return DistributedCache()

def test_init_success(mock_redis):
    """Testa inicialização com sucesso"""
    mock_redis.ping.return_value = True
    cache = DistributedCache()
    assert cache.redis == mock_redis
    assert cache.ttl == RedisConfig.DEFAULT_TTL

def test_init_failure(mock_redis):
    """Testa falha na inicialização"""
    mock_redis.ping.side_effect = redis.ConnectionError()
    with pytest.raises(redis.ConnectionError):
        DistributedCache()

def test_serialize_deserialize(cache):
    """Testa serialização e deserialização"""
    data = {"test": "value", "number": 123}
    serialized = cache._serialize(data)
    deserialized = cache._deserialize(serialized)
    assert deserialized == data

def test_get_success(cache, mock_redis):
    """Testa obtenção de valor com sucesso"""
    mock_redis.get.return_value = '{"test": "value"}'
    value = cache.get("test_key")
    assert value == {"test": "value"}
    mock_redis.get.assert_called_once_with("test_key")

def test_get_missing(cache, mock_redis):
    """Testa obtenção de valor inexistente"""
    mock_redis.get.return_value = None
    value = cache.get("missing_key")
    assert value is None
    mock_redis.get.assert_called_once_with("missing_key")

def test_set_success(cache, mock_redis):
    """Testa armazenamento com sucesso"""
    mock_redis.keys.return_value = ["key1", "key2"]
    result = cache.set("test_key", {"test": "value"})
    assert result is True
    mock_redis.set.assert_called_once()

def test_set_custom_ttl(cache, mock_redis):
    """Testa armazenamento com TTL customizado"""
    mock_redis.keys.return_value = ["key1"]
    result = cache.set("test_key", "value", ttl=60)
    assert result is True
    mock_redis.set.assert_called_once_with(
        "test_key",
        '"value"',
        ex=60
    )

def test_delete_success(cache, mock_redis):
    """Testa remoção com sucesso"""
    mock_redis.delete.return_value = 1
    mock_redis.keys.return_value = ["key1"]
    result = cache.delete("test_key")
    assert result is True
    mock_redis.delete.assert_called_once_with("test_key")

def test_delete_missing(cache, mock_redis):
    """Testa remoção de chave inexistente"""
    mock_redis.delete.return_value = 0
    mock_redis.keys.return_value = ["key1"]
    result = cache.delete("missing_key")
    assert result is False
    mock_redis.delete.assert_called_once_with("missing_key")

def test_clear_success(cache, mock_redis):
    """Testa limpeza com sucesso"""
    result = cache.clear()
    assert result is True
    mock_redis.flushdb.assert_called_once()

def test_get_stats(cache, mock_redis):
    """Testa obtenção de estatísticas"""
    mock_redis.info.return_value = {
        "used_memory_human": "1.00M",
        "connected_clients": 1,
        "uptime_in_days": 1
    }
    mock_redis.keys.return_value = ["key1", "key2"]
    
    stats = cache.get_stats()
    assert stats["total_keys"] == 2
    assert stats["used_memory"] == "1.00M"
    assert stats["connected_clients"] == 1
    assert stats["uptime_days"] == 1 