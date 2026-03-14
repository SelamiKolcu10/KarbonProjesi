"""
Agent #3: The Chief Consultant - Strategy Simulator Module
Phase 2: Optimization & Financial Savings Engine

Bu modül, mevcut tesis verisini "Digital Twin" olarak kopyalayıp
belirli parametreleri değiştirerek potansiyel tasarruf senaryolarını
hesaplar. Emisyon hesaplaması için Agent #2 (AuditorEngine) kullanır.

KRİTİK KURAL: Emisyon hesaplama mantığı burada TEKRAR YAZILMAZ.
Her senaryo için yalnızca AuditorEngine.audit() çağrılır.

Desteklenen Senaryolar
----------------------
1. Green Shift (Yenilenebilir Enerji PPA)
   → Elektrik şebeke faktörünü 0'a indirerek %100 yeşil enerji simüle eder.

2. Scrap Maximization (Hurda Çelik Maks.)
   → En yüksek emisyon faktörlü precursor'ı %20 azaltır,
     aynı miktarı hurda çelik ile ikame eder.

3. Process Efficiency (Proses Verimliliği)
   → Elektrik ve doğalgaz tüketimini %5 düşürür.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.agents.auditor.logic import AuditorEngine
from src.agents.auditor.models import AuditOutput, InputPayload, PrecursorInput
from src.agents.auditor.constants import DEFAULT_PRECURSOR_FACTORS

# ---------------------------------------------------------------------------
# Modül Sabitleri
# ---------------------------------------------------------------------------

# Green Shift: Şebeke emisyon faktörü → 0.0 (tam yenilenebilir)
GREEN_GRID_FACTOR: float = 0.0

# Scrap Maximization: En yüksek faktörlü precursor'ı bu oranda azalt
SCRAP_SHIFT_RATIO: float = 0.20  # %20

# Process Efficiency: Enerji tüketimini bu oranda düşür
EFFICIENCY_REDUCTION: float = 0.05  # %5

# Hurda çelik canonical adı (DEFAULT_PRECURSOR_FACTORS ile uyumlu)
SCRAP_MATERIAL_NAME: str = "scrap-steel"

# CAPEX Heuristikleri
GREEN_SHIFT_CAPEX_PER_MWH: float = 800.0   # €/MWh yıllık kapasite
SCRAP_MAX_CAPEX: float = 0.0                # Tedarik zinciri değişikliği, doğrudan CAPEX yok
EFFICIENCY_CAPEX_PER_MWH_SAVED: float = 500.0  # €/MWh tasarruf edilen


# ---------------------------------------------------------------------------
# Veri Modeli
# ---------------------------------------------------------------------------


class Recommendation(BaseModel):
    """
    Tek bir optimizasyon senaryosunun sonucunu temsil eder.

    Alanlar
    -------
    strategy_name : str
        Senaryonun kısa adı (ör. "Green Shift").
    action_plan : str
        Tesisin uygulaması gereken eylemlerin özeti.
    co2_reduction_tons : float
        Senaryo ile elde edilen CO₂ azaltımı (tCO2e).
    annual_savings_eur : float
        Mevcut duruma kıyasla yıllık tahmini mali tasarruf (€).
    implementation_difficulty : Literal["Low", "Medium", "High"]
        Uygulamanın zorluk seviyesi.
    """

    strategy_name: str = Field(..., description="Optimizasyon senaryosunun adı")
    action_plan: str = Field(
        ..., description="Tesisin uygulaması gereken eylemlerin Türkçe özeti"
    )
    co2_reduction_tons: float = Field(
        ...,
        ge=0.0,
        description="Bu senaryo ile azaltılan CO₂ miktarı (tCO2e)",
    )
    annual_savings_eur: float = Field(
        ...,
        description="Mevcut duruma göre yıllık tahmini mali tasarruf (EUR)",
    )
    estimated_capex_eur: float = Field(
        ...,
        ge=0.0,
        description="Tahmini sermaye harcaması / yatırım maliyeti (EUR)",
    )
    payback_period_years: float = Field(
        ...,
        ge=0.0,
        description="Geri ödeme süresi (yıl). CAPEX / yıllık tasarruf. 0 = anında ROI.",
    )
    implementation_difficulty: Literal["Low", "Medium", "High"] = Field(
        ...,
        description=(
            "Uygulama zorluğu: "
            "'Low' = Operasyonel değişiklik yeterli; "
            "'Medium' = Orta yatırım/tedarik gerektirir; "
            "'High' = Tedarik zinciri veya büyük sermaye değişikliği gerektirir."
        ),
    )
    potential_subsidies: List[str] = Field(
        default_factory=list,
        description=(
            "Bu senaryo için eşleşen potansiyel hibe/sübvansiyon programları. "
            "CAPEX = 0 ise boş liste."
        ),
    )

    model_config = ConfigDict(frozen=True)


# ---------------------------------------------------------------------------
# Ana Sınıf
# ---------------------------------------------------------------------------


class StrategySimulator:
    """
    Agent #3 — Strategy Simulator (Optimizasyon Motoru).

    Mevcut tesis verisi üzerinde üç optimizasyon senaryosunu simüle eder
    ve pozitif mali tasarruf sunan önerileri sıralı döndürür.

    Kullanım
    --------
    >>> auditor = AuditorEngine(cbam_phase_factor=0.025)
    >>> simulator = StrategySimulator(auditor)
    >>> baseline = auditor.audit(input_payload)
    >>> recommendations = simulator.run_simulations(input_payload, baseline)
    >>> for rec in recommendations:
    ...     print(f"{rec.strategy_name}: EUR {rec.annual_savings_eur:,.2f} tasarruf")

    Parametreler
    ------------
    auditor : AuditorEngine
        Emisyon hesaplamaları için kullanılacak Agent #2 örneği.
        Aynı cbam_phase_factor ve free_allocation ayarlarını kullanır.
    """

    def __init__(self, auditor: AuditorEngine) -> None:
        self._auditor = auditor

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def run_simulations(
        self,
        current_payload: InputPayload,
        baseline_result: AuditOutput,
    ) -> List[Recommendation]:
        """
        Tüm senaryoları çalıştırır ve tasarruf sunan önerileri döndürür.

        İşlem Akışı
        -----------
        1. Her senaryo için current_payload'ın derin kopyasını oluştur.
        2. Kopyada ilgili parametreyi değiştir.
        3. AuditorEngine ile yeni audit çalıştır.
        4. Tasarrufu hesapla (baseline − simüle edilen maliyet).
        5. Tasarruf > 0 olan senaryoları filtrele ve döndür.

        Parametreler
        ------------
        current_payload : InputPayload
            Tesisin mevcut raporlama dönemine ait operasyonel verisi.
        baseline_result : AuditOutput
            current_payload için zaten hesaplanmış temel audit sonucu.

        Döndürür
        --------
        List[Recommendation]
            Yıllık tasarrufuna göre azalan sırada, yalnızca pozitif tasarruf
            sunan öneriler.
        """
        baseline_liability = baseline_result.financials.effective_liability_eur
        baseline_emissions = baseline_result.emissions.total_emissions

        candidates: List[Recommendation] = []

        # ── Senaryo 1 ────────────────────────────────────────────────────
        rec1 = self._simulate_green_shift(
            current_payload, baseline_liability, baseline_emissions
        )
        if rec1 is not None:
            candidates.append(rec1)

        # ── Senaryo 2 ────────────────────────────────────────────────────
        rec2 = self._simulate_scrap_maximization(
            current_payload, baseline_liability, baseline_emissions
        )
        if rec2 is not None:
            candidates.append(rec2)

        # ── Senaryo 3 ────────────────────────────────────────────────────
        rec3 = self._simulate_process_efficiency(
            current_payload, baseline_liability, baseline_emissions
        )
        if rec3 is not None:
            candidates.append(rec3)

        # Yalnızca pozitif tasarruf olanları, tasarruf büyüklüğüne göre sırala
        return sorted(
            [r for r in candidates if r.annual_savings_eur > 0],
            key=lambda r: r.annual_savings_eur,
            reverse=True,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Senaryo Implementasyonları
    # ──────────────────────────────────────────────────────────────────────

    def _simulate_green_shift(
        self,
        current_payload: InputPayload,
        baseline_liability: float,
        baseline_emissions: float,
    ) -> Optional[Recommendation]:
        """
        Senaryo 1: Green Shift — %100 Yenilenebilir Enerji PPA

        Yaklaşım
        --------
        Elektrik şebeke emisyon faktörünü 0.0'a düşürerek tüm satın
        alınan elektriğin yenilenebilir PPA (Güç Satın Alma Anlaşması)
        ile karşılandığını simüle eder. Kömür/gaz tüketimi değişmez.

        Uygulama Zorluğu: Medium
        """
        sim_payload = copy.deepcopy(current_payload)

        # AuditorEngine, overrides['grid_factor'] ile şebeke faktörünü değiştirir
        updated_overrides = dict(sim_payload.overrides or {})
        updated_overrides["grid_factor"] = GREEN_GRID_FACTOR

        sim_payload = sim_payload.model_copy(update={"overrides": updated_overrides})

        sim_result = self._auditor.audit(sim_payload)

        savings = round(
            baseline_liability - sim_result.financials.effective_liability_eur, 2
        )
        co2_reduction = round(
            baseline_emissions - sim_result.emissions.total_emissions, 2
        )

        capex = round(current_payload.electricity_consumption_mwh * GREEN_SHIFT_CAPEX_PER_MWH, 2)
        payback = round(capex / savings, 2) if savings > 0 else 0.0

        # Grant Matchmaker: Green Shift senaryosu için hibe eşleştirmesi
        subsidies: List[str] = []
        if capex > 0:
            subsidies = [
                "EBRD Green Economy Financing Facility (GEFF) - Up to 15% Cashback",
                "World Bank Renewable Energy Grant",
            ]

        return Recommendation(
            strategy_name="Green Shift (Yenilenebilir Enerji PPA)",
            action_plan=(
                "Elektrik tedarikini %100 yenilenebilir kaynaklı PPA sözleşmesine geçirin. "
                "Bu sayede Scope 2 (dolaylı) emisyonlar sıfıra indirilir ve "
                "CBAM beyannamenizdeki elektrik kaynaklı karbon yükü ortadan kalkar. "
                f"Tahmini CO\u2082 azaltımı: {co2_reduction:.1f} tCO\u2082e."
            ),
            co2_reduction_tons=max(0.0, co2_reduction),
            annual_savings_eur=savings,
            estimated_capex_eur=capex,
            payback_period_years=payback,
            implementation_difficulty="Medium",
            potential_subsidies=subsidies,
        )

    def _simulate_scrap_maximization(
        self,
        current_payload: InputPayload,
        baseline_liability: float,
        baseline_emissions: float,
    ) -> Optional[Recommendation]:
        """
        Senaryo 2: Scrap Maximization — Hurda Çelik İkamesi

        Yaklaşım
        --------
        Mevcut precursor listesinden en yüksek emisyon faktörüne sahip
        malzemenin miktarını %20 azaltır, eşdeğer miktarı hurda çelik
        ile ikame eder. Hurda çelik'in faktörü (0.35 tCO2e/ton) diğer
        alaşım malzemelerinden çok daha düşüktür.

        Precursor listesi boşsa veya hurda çelik zaten tek malzemeyse
        None döndürür.

        Uygulama Zorluğu: High (tedarik zinciri değişikliği gerektirir)
        """
        if not current_payload.precursors:
            return None

        # Hurda çelik dışındaki en yüksek faktörlü precursor'ı bul
        non_scrap = [
            p
            for p in current_payload.precursors
            if p.material_name.lower() != SCRAP_MATERIAL_NAME
        ]
        if not non_scrap:
            return None  # Sadece hurda çelik var, ikame edilecek hedef yok

        # Emisyon faktörü en yüksek olanı seç (None ise CBAM default kullan)
        target = max(
            non_scrap,
            key=lambda p: (
                p.embedded_emissions_factor
                if p.embedded_emissions_factor is not None
                else DEFAULT_PRECURSOR_FACTORS.get(p.material_name.lower(), 0.0)
            ),
        )

        shift_qty = round(target.quantity_ton * SCRAP_SHIFT_RATIO, 4)

        # Hedef precursor'un miktarını %20 azalt
        updated_target = PrecursorInput(
            material_name=target.material_name,
            quantity_ton=round(target.quantity_ton - shift_qty, 4),
            embedded_emissions_factor=target.embedded_emissions_factor,
        )

        # Hurda çelik girişini bul veya yeni oluştur
        existing_scrap = next(
            (
                p
                for p in current_payload.precursors
                if p.material_name.lower() == SCRAP_MATERIAL_NAME
            ),
            None,
        )

        if existing_scrap is not None:
            updated_scrap = PrecursorInput(
                material_name=existing_scrap.material_name,
                quantity_ton=round(existing_scrap.quantity_ton + shift_qty, 4),
                embedded_emissions_factor=existing_scrap.embedded_emissions_factor,
            )
        else:
            updated_scrap = PrecursorInput(
                material_name=SCRAP_MATERIAL_NAME,
                quantity_ton=shift_qty,
                embedded_emissions_factor=None,  # CBAM default (0.35) kullanılacak
            )

        # Yeni precursor listesini oluştur
        new_precursors: List[PrecursorInput] = []
        for p in current_payload.precursors:
            if p.material_name == target.material_name:
                new_precursors.append(updated_target)
            elif p.material_name.lower() == SCRAP_MATERIAL_NAME:
                new_precursors.append(updated_scrap)
            else:
                new_precursors.append(p)

        # Hurda çelik listede yoksa ekle
        if existing_scrap is None:
            new_precursors.append(updated_scrap)

        sim_payload = copy.deepcopy(current_payload).model_copy(
            update={"precursors": new_precursors}
        )

        sim_result = self._auditor.audit(sim_payload)

        savings = round(
            baseline_liability - sim_result.financials.effective_liability_eur, 2
        )
        co2_reduction = round(
            baseline_emissions - sim_result.emissions.total_emissions, 2
        )

        capex = SCRAP_MAX_CAPEX
        payback = 0.0  # Doğrudan CAPEX yok → anında ROI

        # Grant Matchmaker: CAPEX = 0 için hibe eşleştirmesi yok
        subsidies: List[str] = []

        return Recommendation(
            strategy_name="Scrap Maximization (Hurda Çelik Maks.)",
            action_plan=(
                f"'{target.material_name}' precursor kullanımını "
                f"%{SCRAP_SHIFT_RATIO * 100:.0f} oranında azaltın ({shift_qty:.2f} ton) "
                f"ve bu miktarı düşük-karbon hurda çelik ile ikame edin. "
                "Hurda çeliğin gömülü emisyon faktörü (0.35 tCO\u2082e/ton) "
                f"hedefteki malzemenin faktörüne kıyasla çok daha düşüktür. "
                f"Tahmini CO\u2082 azaltımı: {co2_reduction:.1f} tCO\u2082e."
            ),
            co2_reduction_tons=max(0.0, co2_reduction),
            annual_savings_eur=savings,
            estimated_capex_eur=capex,
            payback_period_years=payback,
            implementation_difficulty="High",
            potential_subsidies=subsidies,
        )

    def _simulate_process_efficiency(
        self,
        current_payload: InputPayload,
        baseline_liability: float,
        baseline_emissions: float,
    ) -> Optional[Recommendation]:
        """
        Senaryo 3: Process Efficiency — Enerji Verimliliği

        Yaklaşım
        --------
        Elektrik ve doğalgaz tüketimini %5 azaltarak muhtemel tasarrufu
        tahmin eder. Bu, değişken hız sürücüleri, ısı geri kazanımı veya
        operasyonel iyileştirmeler ile kolayca elde edilebilir.

        Uygulama Zorluğu: Low (operasyonel optimizasyon yeterli)
        """
        new_electricity = round(
            current_payload.electricity_consumption_mwh * (1 - EFFICIENCY_REDUCTION), 4
        )
        new_gas = round(
            (current_payload.natural_gas_consumption_m3 or 0.0) * (1 - EFFICIENCY_REDUCTION),
            4,
        )

        sim_payload = copy.deepcopy(current_payload).model_copy(
            update={
                "electricity_consumption_mwh": new_electricity,
                "natural_gas_consumption_m3": new_gas,
            }
        )

        sim_result = self._auditor.audit(sim_payload)

        savings = round(
            baseline_liability - sim_result.financials.effective_liability_eur, 2
        )
        co2_reduction = round(
            baseline_emissions - sim_result.emissions.total_emissions, 2
        )

        mwh_saved = current_payload.electricity_consumption_mwh * EFFICIENCY_REDUCTION
        capex = round(mwh_saved * EFFICIENCY_CAPEX_PER_MWH_SAVED, 2)
        payback = round(capex / savings, 2) if savings > 0 else 0.0

        # Grant Matchmaker: Process Efficiency senaryosu için hibe eşleştirmesi
        subsidies: List[str] = []
        if capex > 0:
            subsidies = ["National Energy Efficiency (VAP) Subsidies"]

        return Recommendation(
            strategy_name="Process Efficiency (Enerji Verimliliği)",
            action_plan=(
                f"Elektrik tüketimini {current_payload.electricity_consumption_mwh:.1f} MWh'den "
                f"{new_electricity:.1f} MWh'e, "
                f"doğalgaz tüketimini {current_payload.natural_gas_consumption_m3 or 0.0:.0f} m\u00b3'ten "
                f"{new_gas:.0f} m\u00b3'e düşürecek %{EFFICIENCY_REDUCTION * 100:.0f} verimlilik iyileştirmesi uygulayın. "
                "Değişken hız sürücüleri (VFD), ısı geri kazanım sistemleri veya "
                "operasyonel planlama optimizasyonları bu hedefe ulaşmak için yeterlidir. "
                f"Tahmini CO\u2082 azaltımı: {co2_reduction:.1f} tCO\u2082e."
            ),
            co2_reduction_tons=max(0.0, co2_reduction),
            annual_savings_eur=savings,
            estimated_capex_eur=capex,
            payback_period_years=payback,
            implementation_difficulty="Low",
            potential_subsidies=subsidies,
        )
