"""Logging utilities"""

import sys
from typing import Optional


class Logger:
    """Simple colored logger"""

    COLORS = {
        'OK': '\033[92m',
        'WARN': '\033[93m',
        'ERROR': '\033[91m',
        'INFO': '\033[94m',
        'RESET': '\033[0m'
    }

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def _print(self, level: str, message: str):
        if not self.verbose and level not in ['ERROR', 'WARN']:
            return
        color = self.COLORS.get(level, '')
        reset = self.COLORS['RESET']
        prefix = f"[{level}]"
        print(f"{color}{prefix}{reset} {message}")

    def ok(self, message: str):
        self._print('OK', message)

    def warn(self, message: str):
        self._print('WARN', message)

    def error(self, message: str):
        self._print('ERROR', message)

    def info(self, message: str):
        self._print('INFO', message)
