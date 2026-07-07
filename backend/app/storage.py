"""
In-memory repository with optional JSON file persistence.

This is a minimal skeleton. Task-specific read/write logic and
JSON file dump/load behavior will be implemented in a later
development phase.
"""
from typing import Any, Dict


class InMemoryStorage:
    """A simple in-memory key-value store used as the basis
    for the future task repository."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def all(self) -> Dict[str, Any]:
        return self._data

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
