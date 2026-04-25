"""Small admission control helper for WebSocket streams."""

from __future__ import annotations

from threading import Lock


class StreamLimiter:
    def __init__(self, max_connections: int) -> None:
        self.max_connections = max(1, max_connections)
        self._active = 0
        self._lock = Lock()

    @property
    def active_connections(self) -> int:
        with self._lock:
            return self._active

    def try_acquire(self) -> bool:
        with self._lock:
            if self._active >= self.max_connections:
                return False
            self._active += 1
            return True

    def release(self) -> None:
        with self._lock:
            self._active = max(0, self._active - 1)
