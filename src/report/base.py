"""Base report class"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseReport(ABC):
    """Base class for report generators"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @abstractmethod
    def generate(self) -> str:
        """Generate report content"""
        pass

    @abstractmethod
    def save(self, filepath: str) -> str:
        """Save report to file"""
        pass
