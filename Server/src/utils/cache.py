"""
🚀 PERFORMANCE OPTIMIZATION - Встроенный кэш для API

Простая, но эффективная система кэширования:
- In-memory кэш (не требует Redis)
- TTL (Time To Live) для автоматического истечения
- Потокобезопасность
- Минимальные накладные расходы
"""

import time
import functools
import threading
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta


class CacheEntry:
    """Запись в кэше с TTL"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Проверить, истекла ли запись"""
        elapsed = time.time() - self.created_at
        return elapsed > self.ttl_seconds
    
    def age_ms(self) -> float:
        """Возраст в миллисекундах"""
        return (time.time() - self.created_at) * 1000


class SimpleCache:
    """Простая in-memory кэш с TTL"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Установить значение в кэш"""
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Проверить TTL
            if entry.is_expired():
                del self._cache[key]
                self._stats['evictions'] += 1
                self._stats['misses'] += 1
                return None
            
            self._stats['hits'] += 1
            return entry.value
    
    def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Удалить все истекшие записи"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats['evictions'] += 1
            return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Получить статистику кэша"""
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'total_requests': total,
                'hit_rate_percent': hit_rate,
                'size': len(self._cache)
            }
    
    def reset_stats(self) -> None:
        """Сбросить статистику"""
        with self._lock:
            for key in self._stats:
                self._stats[key] = 0


# Глобальный экземпляр кэша
_cache = SimpleCache()


def cache_result(ttl_seconds: int = 300, key_prefix: str = "") -> Callable:
    """
    Декоратор для кэширования результатов функции
    
    Args:
        ttl_seconds: Время жизни записи в кэше (секунды)
        key_prefix: Префикс для ключа кэша
    
    Example:
        @cache_result(ttl_seconds=60, key_prefix="workstations")
        def get_workstations_list():
            return expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Проверяем кэш
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Вычисляем и кэшируем
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: Optional[str] = None) -> None:
    """
    Инвалидировать кэш
    
    Args:
        pattern: Если None, очищает весь кэш.
                Если строка, удаляет ключи начинающиеся с этой строки.
    """
    if pattern is None:
        _cache.clear()
    else:
        with _cache._lock:
            keys_to_delete = [
                key for key in _cache._cache.keys()
                if key.startswith(pattern)
            ]
            for key in keys_to_delete:
                del _cache._cache[key]


def get_cache() -> SimpleCache:
    """Получить экземпляр кэша"""
    return _cache


def get_cache_stats() -> dict:
    """Получить статистику кэша"""
    return _cache.get_stats()
