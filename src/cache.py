"""Caching layer cho model predictions, expert system, và database queries."""

from hashlib import md5
from typing import Any, Callable, Dict, Optional
import json


class PredictionCache:
    """Cache cho model predictions dựa trên input scores."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _hash_scores(scores: dict) -> str:
        """Tạo hash từ dictionary scores."""
        sorted_items = sorted(scores.items())
        json_str = json.dumps(sorted_items)
        return md5(json_str.encode()).hexdigest()

    def get(self, scores: dict) -> Optional[dict]:
        """Lấy cached prediction."""
        key = self._hash_scores(scores)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, scores: dict, prediction: dict) -> None:
        """Lưu prediction vào cache."""
        if len(self.cache) >= self.max_size:
            # Xóa entry cũ nhất (simple FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        key = self._hash_scores(scores)
        self.cache[key] = prediction

    def clear(self) -> None:
        """Xóa tất cả cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict:
        """Trả về cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "max_size": self.max_size,
        }


class RulesCache:
    """Cache cho expert system rules (lưu tất cả rules vào memory)."""
    
    def __init__(self):
        self._all_rules: Optional[list] = None
        self._rules_by_major: Optional[Dict[str, list]] = None
        self._is_dirty = True

    def load(self, rules: list) -> None:
        """Tải tất cả rules vào cache."""
        self._all_rules = rules
        self._build_index()
        self._is_dirty = False

    def get_all(self) -> list:
        """Lấy tất cả rules từ cache."""
        return self._all_rules or []

    def get_by_major(self, major: str) -> list:
        """Lấy rules cho một chuyên ngành (indexed search)."""
        if not self._rules_by_major:
            self._build_index()
        return self._rules_by_major.get(major, [])

    def _build_index(self) -> None:
        """Build index rules theo major để tối ưu truy vấn."""
        self._rules_by_major = {}
        for rule in (self._all_rules or []):
            if rule.get("active", True):
                major = rule.get("target_major")
                if major not in self._rules_by_major:
                    self._rules_by_major[major] = []
                self._rules_by_major[major].append(rule)

    def invalidate(self) -> None:
        """Invalidate cache (sử dụng khi rules thay đổi)."""
        self._all_rules = None
        self._rules_by_major = None
        self._is_dirty = True

    def is_valid(self) -> bool:
        """Check xem cache còn valid không."""
        return not self._is_dirty


class QueryCache:
    """Cache cho database queries."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, query_key: str) -> Optional[Any]:
        """Lấy cached query result."""
        import time
        if query_key in self.cache:
            result, timestamp = self.cache[query_key]
            if time.time() - timestamp < self.ttl_seconds:
                return result
            else:
                del self.cache[query_key]
        return None

    def set(self, query_key: str, result: Any) -> None:
        """Cache query result."""
        import time
        self.cache[query_key] = (result, time.time())

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()


# Global cache instances
prediction_cache = PredictionCache(max_size=1000)
rules_cache = RulesCache()
query_cache = QueryCache(ttl_seconds=300)


def cached_function(max_size: int = 128) -> Callable:
    """Decorator cho caching functions (alternative to lru_cache)."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        def wrapper(*args, **kwargs) -> Any:
            # Create key từ args và kwargs
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                return cache[key]
            
            if len(cache) >= max_size:
                # Remove oldest entry
                first_key = next(iter(cache))
                del cache[first_key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {"size": len(cache), "max_size": max_size}
        return wrapper
    
    return decorator
