#!/usr/bin/env python3
"""
Performance optimizations for Time Warp II.

Provides expression evaluation caching used by the interpreter.
"""

import threading
from typing import Dict, Any, Optional


class ExpressionCache:
    """Cache for compiled expressions to avoid re-evaluation."""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value for key."""
        with self._lock:
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def put(self, key: str, value: Any) -> None:
        """Store value in cache."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entries (simple FIFO)
                oldest_keys = list(self.cache.keys())[:self.max_size // 10]
                for k in oldest_keys:
                    del self.cache[k]

            self.cache[key] = value

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }
