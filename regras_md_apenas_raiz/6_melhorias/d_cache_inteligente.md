# Cache Inteligente

## Descrição
Sistema de cache para otimizar consultas frequentes

## Implementação
```python
from cachetools import LRUCache

class SmartCache:

    def __init__(self, max_size):
        self.cache = LRUCache(max_size)

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
```
