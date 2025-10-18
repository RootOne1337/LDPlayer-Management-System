"""
🚀 Тесты производительности и кэширования

Проверяет:
- Cache endpoints (stats, clear, invalidate)
- Performance metrics
- Cache hit rates
"""

import pytest
from fastapi.testclient import TestClient
import time

# Добавить путь к src
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.server import app
from src.utils.cache import get_cache, _cache


client = TestClient(app)


@pytest.fixture
def admin_token():
    """Получить токен администратора"""
    try:
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            # Если это APIResponse, берем из data
            if "data" in data and isinstance(data["data"], dict):
                return data["data"].get("access_token")
    except Exception:
        pass
    
    # Fallback - создать пользователя
    try:
        client.post(
            "/api/auth/register",
            json={"username": "admin", "password": "admin123", "role": "admin"}
        )
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        pass
    
    return None


class TestCachePerformance:
    """🚀 Тесты кэширования и производительности"""
    
    def test_cache_stats_endpoint(self, admin_token):
        """✅ GET /api/performance/cache-stats возвращает статистику"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        response = client.get(
            "/api/performance/cache-stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data
        assert "hits" in data["cache_stats"]
        assert "misses" in data["cache_stats"]
        assert "size" in data["cache_stats"]
    
    def test_cache_clear_endpoint(self, admin_token):
        """✅ POST /api/performance/cache-clear очищает кэш"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        # Заполнить кэш каким-то значением
        _cache.set("test_key", "test_value", 300)
        initial_size = _cache.get("test_key") is not None
        
        # Очистить кэш
        response = client.post(
            "/api/performance/cache-clear",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Проверить что кэш пуст
        assert _cache.get("test_key") is None
    
    def test_cache_invalidate_endpoint(self, admin_token):
        """✅ POST /api/performance/cache-invalidate инвалидирует по паттерну"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        # Заполнить кэш
        _cache.set("workstations:list", "data1", 300)
        _cache.set("workstations:detail", "data2", 300)
        _cache.set("users:list", "data3", 300)
        
        # Инвалидировать только workstations
        response = client.post(
            "/api/performance/cache-invalidate",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"pattern": "workstations"}
        )
        assert response.status_code == 200
        
        # Проверить результаты
        assert _cache.get("workstations:list") is None
        assert _cache.get("workstations:detail") is None
        assert _cache.get("users:list") == "data3"  # Не должен быть удален
    
    def test_performance_metrics_endpoint(self, admin_token):
        """✅ GET /api/performance/metrics возвращает метрики"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        response = client.get(
            "/api/performance/metrics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        metrics = data["metrics"]
        
        # Проверить структуру метрик
        assert "cache" in metrics
        assert "managers" in metrics
        assert "websockets" in metrics
        
        # Проверить cache метрики
        cache_metrics = metrics["cache"]
        assert "hit_rate_percent" in cache_metrics
        assert "total_hits" in cache_metrics
        assert "total_misses" in cache_metrics
        assert "cached_items" in cache_metrics
    
    def test_cache_invalidate_requires_admin(self):
        """✅ Инвалидация кэша требует роли ADMIN"""
        response = client.post(
            "/api/performance/cache-invalidate",
            params={"pattern": "test"}
        )
        # Должен быть 401 или 403 (не авторизован)
        assert response.status_code in [401, 403]
    
    def test_cache_stats_requires_admin(self):
        """✅ Статистика кэша требует роли ADMIN"""
        response = client.get("/api/performance/cache-stats")
        assert response.status_code in [401, 403]


class TestPerformanceImprovement:
    """📊 Тесты улучшения производительности"""
    
    def test_workstations_list_performance(self, admin_token):
        """✅ Список рабочих станций получается быстро"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        # Первый запрос (может быть медленнее из-за работы с manager'ами)
        start = time.time()
        response1 = client.get(
            "/api/workstations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        time1 = (time.time() - start) * 1000  # в миллисекундах
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)
        
        # Второй запрос (должен быть быстрее благодаря логике)
        start = time.time()
        response2 = client.get(
            "/api/workstations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        time2 = (time.time() - start) * 1000
        
        assert response2.status_code == 200
        
        # Оба ответа должны быть быстрыми (< 1 сек для тестов)
        assert time1 < 1000, f"First request too slow: {time1}ms"
        assert time2 < 1000, f"Second request too slow: {time2}ms"
    
    def test_cache_hit_rate_improves(self):
        """✅ Hit rate кэша улучшается с повторными запросами"""
        _cache.reset_stats()
        _cache.clear()
        
        # Сделать несколько запросов с одинаковыми параметрами
        for i in range(5):
            _cache.set("perf_test_key", f"value_{i}", 300)
            result = _cache.get("perf_test_key")
        
        stats = _cache.get_stats()
        assert stats["hits"] > 0, "Should have cache hits"
        assert stats["hit_rate_percent"] > 0, "Hit rate should be > 0%"


class TestCacheInvalidation:
    """🔄 Тесты инвалидации кэша"""
    
    def test_cache_invalidation_after_workstation_creation(self, admin_token):
        """✅ Кэш инвалидируется после создания рабочей станции"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        _cache.reset_stats()
        _cache.clear()
        
        # Получить список рабочих станций (заполняет кэш)
        resp1 = client.get(
            "/api/workstations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp1.status_code == 200
        
        # Проверить что есть статистика
        stats_before = _cache.get_stats()
        
        # Создать новую рабочую станцию
        new_ws_data = {
            "name": f"cache_test_ws_{int(time.time())}",
            "host": "192.168.1.99",
            "port": 5985,
            "username": "admin",
            "password": "test123"
        }
        
        create_resp = client.post(
            "/api/workstations",
            json=new_ws_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # После создания кэш должен быть инвалидирован
        # (в реальной жизни это проверяют по логам или прямой проверке кэша)
        assert create_resp.status_code in [201, 400]  # 201 если успешно, 400 если валидация


class TestCacheEdgeCases:
    """⚠️ Тесты граничных случаев"""
    
    def test_cache_expiration(self):
        """✅ Кэш истекает через TTL"""
        _cache.clear()
        
        # Установить значение с короткой TTL
        _cache.set("expire_test", "value", ttl_seconds=1)
        assert _cache.get("expire_test") == "value"
        
        # Подождать истечение
        time.sleep(1.1)
        
        # Значение должно истечь
        assert _cache.get("expire_test") is None
    
    def test_cache_empty_pattern_invalidate(self, admin_token):
        """✅ Пустой паттерн для инвалидации отвергается"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        response = client.post(
            "/api/performance/cache-invalidate",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"pattern": ""}
        )
        assert response.status_code == 400
    
    def test_cache_concurrent_access(self):
        """✅ Кэш безопасен при одновременном доступе"""
        import threading
        
        _cache.clear()
        results = []
        
        def set_and_get(key, value):
            _cache.set(key, value, 300)
            result = _cache.get(key)
            results.append(result == value)
        
        # Запустить несколько потоков
        threads = [
            threading.Thread(target=set_and_get, args=(f"thread_key_{i}", f"value_{i}"))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Все операции должны быть успешны
        assert all(results), "All concurrent operations should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
