"""
Agent #2: The Auditor Engine
CBAM Compliance & Financial Impact Assessment

Bu modül Agent #1'den gelen veriyi işler, fizik bazlı validasyon yapar,
Scope 1 & 2 emisyonları hesaplar ve mali yükümlülüğü tahmin eder.
"""

from .models import InputPayload, AuditOutput, AnomalyFlag, AuditLogEntry, ProcessInputs, PrecursorInput
from .logic import AuditorEngine

__all__ = [
    'InputPayload',
    'AuditOutput',
    'AnomalyFlag',
    'AuditLogEntry',
    'AuditorEngine',
    'ProcessInputs',
    'PrecursorInput',
]

__version__ = '1.0.0'
