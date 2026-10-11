"""Настройки читаются из окружения в config.py.

Модуль оставлен, чтобы импорт ADMIN_EMAIL / ADMIN_PASSWORD не сломался.
"""

from config import ADMIN_EMAIL, ADMIN_PASSWORD

__all__ = ["ADMIN_EMAIL", "ADMIN_PASSWORD"]
