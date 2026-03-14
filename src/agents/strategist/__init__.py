"""
Agent #3: The Chief Consultant
CBAM Strategic Advisory & Compliance Intelligence

Bu modül, Agent #2'nin ürettiği AuditResult'ı işler ve
gerçek bir AB denetçisi gibi davranarak uyumluluk durumunu değerlendirir.

Modüller:
- compliance_guard : Hazırlık & Risk değerlendirmesi (Phase 1)
- simulator        : Optimizasyon & Tasarruf Simülasyonu (Phase 2)
- chief_consultant : Orkestratör & Yönetici Raporu (Phase 3)
"""

from .compliance_guard import ComplianceGuard, ComplianceRiskReport
from .simulator import StrategySimulator, Recommendation
from .chief_consultant import ChiefConsultantAgent, ExecutiveConsultingReport

__all__ = [
    "ComplianceGuard",
    "ComplianceRiskReport",
    "StrategySimulator",
    "Recommendation",
    "ChiefConsultantAgent",
    "ExecutiveConsultingReport",
]

__version__ = "3.0.0"
