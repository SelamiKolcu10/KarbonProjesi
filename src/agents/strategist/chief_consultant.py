"""
Agent #3: The Chief Consultant - Executive Orchestrator
Phase 3: Final Integration & Executive Report Generation

Bu modül, Agent #3 sisteminin ana giriş noktasıdır.
ComplianceGuard (risk) ve StrategySimulator (tasarruf) modüllerini
tek bir akışta orkestre ederek yönetici seviyesinde bir JSON raporu üretir.

Akış
----
1. AuditorEngine ile temel (baseline) denetim sonucunu hesapla.
2. ComplianceGuard ile uyumluluk risk değerlendirmesini yap.
3. StrategySimulator ile optimizasyon senaryolarını simüle et.
4. Sonuçları birleştirip AI Danışman Özeti oluştur.
5. ExecutiveConsultingReport döndür.

Kullanım
--------
>>> from src.agents.strategist.chief_consultant import ChiefConsultantAgent
>>> consultant = ChiefConsultantAgent()
>>> report = consultant.generate_report(payload)
>>> print(report.model_dump_json(indent=2))
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.agents.auditor.logic import AuditorEngine
from src.agents.auditor.models import AuditOutput, InputPayload
from src.agents.auditor.constants import CBAM_PHASE_2026, FREE_ALLOCATION_DEFAULT, ETS_PRICE_PER_TON_CO2

from .compliance_guard import ComplianceGuard, ComplianceRiskReport
from .simulator import StrategySimulator, Recommendation

# ---------------------------------------------------------------------------
# CBAM Phase-in Takvimi (AB Tüzüğü 2023/956, Madde 36)
# ---------------------------------------------------------------------------

CBAM_PHASE_SCHEDULE: Dict[int, float] = {
    2026: 0.025,   # %2.5
    2027: 0.050,   # %5.0
    2028: 0.100,   # %10.0
    2029: 0.225,   # %22.5
    2030: 0.485,   # %48.5
}


# ---------------------------------------------------------------------------
# Veri Modeli
# ---------------------------------------------------------------------------


class ExecutiveConsultingReport(BaseModel):
    """
    Agent #3 sisteminin nihai çıktısı.

    Tesis yöneticilerine ve CBAM sorumlularına sunulmak üzere tasarlanmış
    yönetici seviyesinde bir danışmanlık raporu.

    Alanlar
    -------
    facility_name : str
        Raporun ait olduğu tesisin adı.
    reporting_period : str
        Denetim dönemi (ör. "2026-Q1", "2026-02").
    audit_summary : dict
        Temel denetim sonuçları — toplam emisyon, mali yükümlülük vb.
    compliance_risk : ComplianceRiskReport
        Phase 1 çıktısı — hazırlık skoru, eksik alanlar, ceza tahmini.
    top_recommendations : List[Recommendation]
        Phase 2 çıktısı — yıllık tasarrufa göre azalan sıralı öneriler.
    ai_consultant_summary : str
        En büyük risk ve en büyük fırsatı özetleyen dinamik metin.
    generated_at : datetime
        Raporun oluşturulma zamanı.
    agent_version : str
        Chief Consultant modül sürümü.
    """

    facility_name: str = Field(
        ..., description="Raporun ait olduğu tesisin adı"
    )
    reporting_period: str = Field(
        ..., description="Denetim dönemi (ör. '2026-Q1')"
    )
    audit_summary: Dict[str, Any] = Field(
        ...,
        description=(
            "Temel denetim verileri: toplam emisyon (tCO2e), "
            "Scope 1/2 ayrımı, mali yükümlülük (EUR), uyumluluk durumu"
        ),
    )
    compliance_risk: ComplianceRiskReport = Field(
        ..., description="ComplianceGuard tarafından üretilen risk raporu"
    )
    top_recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Yıllık tasarrufa göre azalan sıralı optimizasyon önerileri",
    )
    five_year_projection: Dict[int, float] = Field(
        ...,
        description=(
            "CBAM 5 yıllık mali projeksiyon. "
            "Yıl bazında tam karbon vergisi yükümlülüğünün phase-in oranıyla çarpımı (EUR). "
            "Ör: {2026: 973.15, 2027: 1946.29, ...}"
        ),
    )
    stress_test_scenarios: Dict[str, float] = Field(
        default_factory=dict,
        description=(
            "ETS fiyat volatilitesi stres testi sonuçları. "
            "Üç senaryo altında toplam vergi yükümlülüğü (EUR): "
            "'Base Case', 'Best Case' (-20%), 'Worst Case' (+30%)."
        ),
    )
    ai_consultant_summary: str = Field(
        ...,
        description=(
            "AI Danışman Özeti — en büyük risk ve en iyi fırsatı "
            "tek paragrafta özetleyen yönetici metni"
        ),
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Raporun oluşturulma zamanı",
    )
    agent_version: str = Field(
        default="3.0.0",
        description="Chief Consultant Agent sürümü",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facility_name": "ABC Döküm Sanayi",
                "reporting_period": "2026-02",
                "audit_summary": {
                    "total_emissions_tco2e": 117.81,
                    "scope_1_direct": 31.81,
                    "scope_2_indirect": 86.00,
                    "effective_liability_eur": 250.34,
                    "is_compliant": True,
                },
                "ai_consultant_summary": "Tesis uyumlu durumda...",
            }
        },
    )


# ---------------------------------------------------------------------------
# Ana Sınıf
# ---------------------------------------------------------------------------


class ChiefConsultantAgent:
    """
    Agent #3 — The Chief Consultant (Orkestratör).

    ComplianceGuard ve StrategySimulator modüllerini koordine ederek
    tek bir API çağrısıyla kapsamlı danışmanlık raporu üretir.

    Parametreler
    ------------
    strict_physics : bool
        AuditorEngine'e aktarılır. True ise kritik fizik ihlallerinde hata fırlatır.
    cbam_phase_factor : float
        CBAM geçiş dönemi katsayısı (0.0–1.0). AuditorEngine'e aktarılır.
    free_allocation : float
        Ücretsiz tahsisat miktarı (tCO2e). AuditorEngine'e aktarılır.
    penalty_rate : float
        ComplianceGuard ceza oranı (€/tCO2e). Varsayılan: 20.0
    """

    def __init__(
        self,
        strict_physics: bool = False,
        cbam_phase_factor: float = CBAM_PHASE_2026,
        free_allocation: float = FREE_ALLOCATION_DEFAULT,
        penalty_rate: float = 20.0,
    ) -> None:
        # Agent #2 — Denetim Motoru
        self._auditor = AuditorEngine(
            strict_physics=strict_physics,
            cbam_phase_factor=cbam_phase_factor,
            free_allocation=free_allocation,
        )

        # Agent #3 Phase 1 — Risk Değerlendirmesi
        self._guard = ComplianceGuard(penalty_rate=penalty_rate)

        # Agent #3 Phase 2 — Optimizasyon Simülasyonu
        self._simulator = StrategySimulator(self._auditor)

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def generate_report(
        self,
        payload: InputPayload,
        ets_price_override: Optional[float] = None,
    ) -> ExecutiveConsultingReport:
        """
        Tam danışmanlık raporu üretir.

        Adımlar
        -------
        1. AuditorEngine ile baseline denetim.
        2. ComplianceGuard ile risk değerlendirmesi.
        3. StrategySimulator ile optimizasyon senaryoları.
        4. Önerileri yıllık tasarrufa göre azalan sırala.
        5. AI Danışman Özetini oluştur.
        6. ExecutiveConsultingReport döndür.

        Parametreler
        ------------
        payload : InputPayload
            Tesisin operasyonel verisi.
        ets_price_override : float, optional
            ETS fiyatı simülasyonu (varsayılan: sabit €85/ton).

        Döndürür
        --------
        ExecutiveConsultingReport
        """
        # ── Adım 1: Baseline Denetim ────────────────────────────────────
        baseline: AuditOutput = self._auditor.audit(
            payload, ets_price_override=ets_price_override
        )

        # ── Adım 2: Risk Değerlendirmesi ────────────────────────────────
        risk_report: ComplianceRiskReport = self._guard.evaluate_readiness(
            payload, baseline
        )

        # ── Adım 3: Optimizasyon Senaryoları ────────────────────────────
        recommendations: List[Recommendation] = self._simulator.run_simulations(
            payload, baseline
        )

        # ── Adım 4: Tasarrufa göre azalan sırala (simulator zaten sıralıyor
        #    ama garanti olarak burada da sıralıyoruz) ────────────────────
        sorted_recommendations = sorted(
            recommendations,
            key=lambda r: r.annual_savings_eur,
            reverse=True,
        )

        # ── Adım 5: Denetim Özeti ───────────────────────────────────────
        audit_summary = self._build_audit_summary(baseline)

        # ── Adım 6: 5 Yıllık CBAM Projeksiyon ("Tsunami Effect") ────────
        total_liability_full_price = baseline.financials.total_liability_eur
        projection = self._calculate_projection(total_liability_full_price)

        # ── Adım 6b: Carbon Price Stress Test ───────────────────────────
        base_ets = ets_price_override or ETS_PRICE_PER_TON_CO2
        stress_test = self._calculate_stress_test(
            total_emissions=baseline.emissions.total_emissions,
            free_allocation=self._auditor.free_allocation,
            cbam_phase_factor=self._auditor.cbam_phase_factor,
            base_ets_price=base_ets,
        )

        # ── Adım 7: AI Danışman Özeti ───────────────────────────────────
        ai_summary = self._generate_ai_summary(
            facility_name=payload.facility_name,
            baseline=baseline,
            risk_report=risk_report,
            recommendations=sorted_recommendations,
            projection=projection,
            stress_test=stress_test,
        )

        # ── Adım 8: Rapor Oluştur ───────────────────────────────────────
        return ExecutiveConsultingReport(
            facility_name=payload.facility_name,
            reporting_period=payload.reporting_period,
            audit_summary=audit_summary,
            compliance_risk=risk_report,
            top_recommendations=sorted_recommendations,
            five_year_projection=projection,
            stress_test_scenarios=stress_test,
            ai_consultant_summary=ai_summary,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Yardımcı Metotlar
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _calculate_projection(
        total_liability_full_price: float,
        start_year: int = 2026,
    ) -> Dict[int, float]:
        """
        CBAM phase-in takvimine göre 5 yıllık mali projeksiyon hesaplar.

        AB, serbest tahsisatları kademeli olarak kaldıracaktır.
        Bu metot, tam karbon vergisinin (indirimler öncesi brüt tutar)
        her yılın phase-in oranıyla çarpımını döndürür.

        Parametreler
        ------------
        total_liability_full_price : float
            Toplam emisyon × ETS fiyatı (phase-in indirimi uygulanmamış brüt tutar).
        start_year : int
            Projeksiyon başlangıç yılı. Varsayılan: 2026.

        Döndürür
        --------
        Dict[int, float]
            {yıl: tahmini_yükümlülük_eur} sözlüğü (5 yıllık).
        """
        projection: Dict[int, float] = {}
        for offset in range(5):
            year = start_year + offset
            factor = CBAM_PHASE_SCHEDULE.get(year, 1.0)
            projection[year] = round(total_liability_full_price * factor, 2)
        return projection

    @staticmethod
    def _calculate_stress_test(
        total_emissions: float,
        free_allocation: float,
        cbam_phase_factor: float,
        base_ets_price: float,
    ) -> Dict[str, float]:
        """
        ETS fiyat volatilitesi stres testi.

        Üç senaryo altında efektif vergi yükümlülüğünü hesaplar:
        - Base Case  : Mevcut ETS fiyatı
        - Best Case   : ETS fiyatı %20 düşük (piyasa rahatlığı)
        - Worst Case  : ETS fiyatı %30 yüksek (piyasa şoku)

        Parametreler
        ------------
        total_emissions : float
            Toplam emisyon (tCO2e).
        free_allocation : float
            Ücretsiz tahsisat (tCO2e).
        cbam_phase_factor : float
            CBAM geçiş dönemi katsayısı.
        base_ets_price : float
            Temel ETS fiyatı (€/tCO2e).

        Döndürür
        --------
        Dict[str, float]
            {"Base Case": €, "Best Case": €, "Worst Case": €}
        """
        net_emissions = max(0.0, total_emissions - free_allocation)

        scenarios = {
            "Base Case": base_ets_price,
            "Best Case": base_ets_price * 0.80,   # -20%
            "Worst Case": base_ets_price * 1.30,  # +30%
        }

        return {
            label: round(net_emissions * price * cbam_phase_factor, 2)
            for label, price in scenarios.items()
        }

    @staticmethod
    def _build_audit_summary(baseline: AuditOutput) -> Dict[str, Any]:
        """
        AuditOutput'tan yönetici seviyesinde özet sözlük oluşturur.
        """
        return {
            "total_emissions_tco2e": round(baseline.emissions.total_emissions, 2),
            "scope_1_direct_tco2e": round(baseline.emissions.scope_1_direct, 2),
            "scope_2_indirect_tco2e": round(baseline.emissions.scope_2_indirect, 2),
            "process_emissions_tco2e": round(baseline.emissions.process_emissions, 2),
            "precursor_emissions_tco2e": round(baseline.emissions.precursor_emissions, 2),
            "emission_intensity_per_ton": round(
                baseline.emissions.emission_intensity_per_ton, 4
            ),
            "total_liability_eur": round(baseline.financials.total_liability_eur, 2),
            "effective_liability_eur": round(
                baseline.financials.effective_liability_eur, 2
            ),
            "ets_price_eur_per_ton": baseline.financials.ets_price_eur_per_ton,
            "cbam_phase_factor": baseline.financials.cbam_phase_factor,
            "is_compliant": baseline.is_compliant,
            "anomaly_count": len(baseline.anomalies),
            "confidence_score": baseline.confidence_score,
        }

    @staticmethod
    def _generate_ai_summary(
        facility_name: str,
        baseline: AuditOutput,
        risk_report: ComplianceRiskReport,
        recommendations: List[Recommendation],
        projection: Optional[Dict[int, float]] = None,
        stress_test: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        En büyük risk ve en iyi fırsatı özetleyen dinamik metin oluşturur.

        Metin yapısı
        ------------
        1. Tesis adı ve uyumluluk durumu.
        2. Hazırlık skoru ve son tarih riski.
        3. Eksik alanlar varsa uyarı.
        4. Tahmini ceza bilgisi.
        5. En iyi öneri ve potansiyel tasarruf.
        """
        lines: List[str] = []

        # ── Uyumluluk durumu ─────────────────────────────────────────────
        compliance_text = "UYUMLU" if baseline.is_compliant else "UYUMSUZ"
        lines.append(
            f"{facility_name} tesisi {baseline.input_summary.get('period', '')} "
            f"donemi icin {compliance_text} olarak degerlendirildi."
        )

        # ── Hazırlık skoru ve son tarih ──────────────────────────────────
        score = risk_report.readiness_score
        deadline = risk_report.deadline_status

        if score >= 90:
            score_label = "mukemmel"
        elif score >= 70:
            score_label = "yeterli"
        elif score >= 50:
            score_label = "dusuk"
        else:
            score_label = "kritik"

        lines.append(
            f"Hazirlik skoru {score:.0f}/100 ({score_label}). "
            f"Son tarih durumu: {deadline}."
        )

        # ── Eksik alanlar ────────────────────────────────────────────────
        missing = risk_report.missing_mandatory_fields
        if missing:
            lines.append(
                f"UYARI: {len(missing)} zorunlu alan eksik — "
                f"{', '.join(missing)}. "
                "Bu alanlar doldurulmadan AB'ye rapor gonderilemez."
            )

        # ── Ceza tahmini ─────────────────────────────────────────────────
        penalty = risk_report.estimated_penalty_eur
        if penalty > 0:
            lines.append(
                f"Mevcut durumda tahmini ceza: EUR {penalty:,.2f}. "
                "Eksiklikleri gidererek bu cezadan kacinilabilir."
            )

        # ── Eşik uyarıları ───────────────────────────────────────────────
        for warning in risk_report.threshold_warnings:
            lines.append(f"ESIK UYARISI: {warning}")

        # ── ETS Fiyat Stres Testi Uyarısı ──────────────────────────
        if stress_test:
            best = stress_test.get("Best Case", 0.0)
            worst = stress_test.get("Worst Case", 0.0)
            base = stress_test.get("Base Case", 0.0)
            volatility_gap = worst - best
            lines.append(
                f"ETS FIYAT STRES TESTI: "
                f"En iyi senaryo EUR {best:,.2f}, "
                f"baz senaryo EUR {base:,.2f}, "
                f"en kotu senaryo EUR {worst:,.2f}."
            )
            if volatility_gap > 10_000:
                lines.append(
                    f"KRITIK VOLATILITE UYARISI: En iyi ve en kotu senaryo arasindaki fark "
                    f"EUR {volatility_gap:,.2f} ile EUR 10,000 esigini asiyor. "
                    "Karbon fiyat riski hedge edilmeli veya uzun vadeli PPA ile sabitlenmelidir."
                )

        # ── 5 Yıllık Projeksiyon Uyarısı ("Tsunami Effect") ────────────
        if projection:
            current_year = min(projection)
            final_year = max(projection)
            current_cost = projection[current_year]
            final_cost = projection[final_year]
            if current_cost > 0:
                growth = final_cost / current_cost
                lines.append(
                    f"CBAM TSUNAMI UYARISI: Mevcut karbon vergisi EUR {current_cost:,.2f} ({current_year}), "
                    f"ancak {final_year} yilinda EUR {final_cost:,.2f} seviyesine yukselecektir "
                    f"({growth:.0f}x artis). Onlem alinmazsa mali yuk katlanarak buyuyecektir."
                )
        # ── En iyi öneri ─────────────────────────────────────────────────
        if recommendations:
            best = recommendations[0]
            lines.append(
                f"EN IYI FIRSAT: '{best.strategy_name}' senaryosu uygulanarak "
                f"yillik EUR {best.annual_savings_eur:,.2f} tasarruf ve "
                f"{best.co2_reduction_tons:.1f} tCO2e emisyon azaltimi "
                f"saglanabilir (uygulama zorlugu: {best.implementation_difficulty})."
            )

            if len(recommendations) > 1:
                total_savings = sum(r.annual_savings_eur for r in recommendations)
                total_co2 = sum(r.co2_reduction_tons for r in recommendations)
                lines.append(
                    f"Tum senaryolar birlikte uygulanirsa toplam "
                    f"EUR {total_savings:,.2f} tasarruf ve "
                    f"{total_co2:.1f} tCO2e azaltim potansiyeli vardir."
                )
        else:
            lines.append(
                "Su an icin ek tasarruf senaryosu tespit edilemedi. "
                "Tesis zaten verimli calisiyor olabilir."
            )

        return " ".join(lines)
