"""
Agent #3: The Chief Consultant - Compliance Guard Module
Phase 1: Readiness & Risk Assessment

Bu modül, bir AB CBAM denetçisi rolünü üstlenerek tesisin raporunu
AB'ye göndermeden önce veri tamlığını, hazırlık skorunu ve
uyumsuzluk durumunda doğacak cezaları değerlendirir.

Temel Görevler:
- Zorunlu alan eksikliği tespiti
- 100 üzerinden hazırlık skoru hesaplama
- CBAM ceza tahmini (€/ton)
- Emisyon eşik uyarıları
- Son tarih durum değerlendirmesi
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.agents.auditor.models import AuditOutput, InputPayload
from src.agents.auditor.constants import DEFAULT_PRECURSOR_FACTORS

# ---------------------------------------------------------------------------
# Modül Sabitleri
# ---------------------------------------------------------------------------

# Eksik/hatalı raporlama için AB CBAM ceza oranı (€/tCO2e)
# Gerçek oran €10–€50 arasındadır; bu MVP için: €20/ton
PENALTY_RATE_EUR_PER_TON: float = 20.0

# Bu eşiğin altındaki hazırlık skoru ceza tetikler
PENALTY_READINESS_THRESHOLD: float = 70.0

# Bu değerin üzerindeki emisyon yoğunluğu (tCO2e/ton çelik) yüksek risk uyarısı verir
HIGH_EMISSION_INTENSITY_THRESHOLD: float = 2.0

# Son tarihe bu kadar gün kala "At Risk" durumuna geçilir
AT_RISK_DAYS: int = 30

# AB "İyi Standart" kıyaslama faktörleri (tCO2e/ton)
# Gerçek tedarikçi faktörü bunlardan yüksekse "kirli tedarik" maliyeti oluşur.
EU_BENCHMARK_FACTORS: dict[str, float] = {
    "pig-iron": 1.90,
    "ferro-manganese": 1.50,
}


# ---------------------------------------------------------------------------
# Veri Modelleri (Pydantic V2)
# ---------------------------------------------------------------------------


class ComplianceRiskReport(BaseModel):
    """
    Compliance Guard modülünün çıktı şeması.

    Bir raporlama dönemi için AB denetçi perspektifinden
    hazırlık durumu ve risk değerlendirmesini temsil eder.
    """

    readiness_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "CBAM veri hazırlık skoru (0–100). "
            "100 = tam ve eksiksiz veri, 0 = raporlanamaz durum."
        ),
    )

    missing_mandatory_fields: List[str] = Field(
        default_factory=list,
        description=(
            "Zorunlu olup eksik veya sıfır olan alanların listesi. "
            "AB CBAM raporlaması için bu alanlar doldurulmalıdır."
        ),
    )

    estimated_penalty_eur: float = Field(
        ...,
        ge=0.0,
        description=(
            "Geç veya eksik rapor durumunda tahmini AB CBAM cezası (EUR). "
            "Hazırlık skoru eşiğin altındaysa veya rapor geç ise hesaplanır."
        ),
    )

    threshold_warnings: List[str] = Field(
        default_factory=list,
        description=(
            "Sektör kıyaslamaları veya AB eşiklerini aşan duruma ilişkin uyarılar. "
            "Örn: 'Yüksek emisyon yoğunluğu — denetim riski yüksek.'"
        ),
    )

    deadline_status: Literal["On Time", "At Risk", "Overdue"] = Field(
        ...,
        description=(
            "Raporlama dönemi için son tarih durumu. "
            "'On Time': Süre var. 'At Risk': 30 günden az kaldı. 'Overdue': Süre geçti."
        ),
    )

    # ── Supplier Benchmark ───────────────────────────────────────────────────
    supplier_benchmark_warnings: List[str] = Field(
        default_factory=list,
        description=(
            "AB kıyaslama faktörlerini aşan tedarikçi uyarıları. "
            "Her uyarı, ilgili malzeme ve ek CBAM maliyetini içerir."
        ),
    )

    cost_of_dirty_supply_eur: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Tedarikçilerin AB kıyaslama değerinin üzerindeki emisyon "
            "faktörleri nedeniyle ödenen ek CBAM vergisi (EUR)."
        ),
    )

    # ── Audit Metadata ──────────────────────────────────────────────────────
    evaluated_at: datetime = Field(
        default_factory=datetime.now,
        description="Bu raporun üretildiği zaman damgası.",
    )

    compliance_guard_version: str = Field(
        default="1.1.0",
        description="Compliance Guard modülünün sürüm numarası.",
    )

    model_config = ConfigDict(frozen=True)


# ---------------------------------------------------------------------------
# Ana Sınıf
# ---------------------------------------------------------------------------


class ComplianceGuard:
    """
    Agent #3 — Compliance Guard (Hazırlık & Risk Modülü).

    Bir AB CBAM denetçisi gibi davranarak tesis raporunu göndermeden önce
    veri kalitesini, eksik alanları ve ceza riskini değerlendirir.

    Kullanım
    --------
    >>> guard = ComplianceGuard()
    >>> report = guard.evaluate_readiness(input_payload, audit_result)
    >>> print(f"Hazırlık Skoru: {report.readiness_score}/100")
    >>> print(f"Tahmini Ceza: €{report.estimated_penalty_eur:,.2f}")

    Parametreler
    ------------
    penalty_rate : float
        Ton başına ceza oranı (€/tCO2e). Varsayılan: €20.0
    readiness_threshold : float
        Bu skorun altında ceza tetiklenir. Varsayılan: 70.0
    high_intensity_threshold : float
        Bu değerin üzerinde emisyon yoğunluğu uyarı verir (tCO2e/ton). Varsayılan: 2.0
    at_risk_days : int
        Son tarihe bu kadar gün kala "At Risk" durumu başlar. Varsayılan: 30
    """

    def __init__(
        self,
        penalty_rate: float = PENALTY_RATE_EUR_PER_TON,
        readiness_threshold: float = PENALTY_READINESS_THRESHOLD,
        high_intensity_threshold: float = HIGH_EMISSION_INTENSITY_THRESHOLD,
        at_risk_days: int = AT_RISK_DAYS,
    ) -> None:
        self.penalty_rate = penalty_rate
        self.readiness_threshold = readiness_threshold
        self.high_intensity_threshold = high_intensity_threshold
        self.at_risk_days = at_risk_days

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def evaluate_readiness(
        self,
        input_payload: InputPayload,
        audit_result: AuditOutput,
    ) -> ComplianceRiskReport:
        """
        Ana giriş noktası. Tüm kontrolleri çalıştırır ve bir
        ComplianceRiskReport döndürür.

        Adımlar
        -------
        1. Zorunlu eksik alanları tespit et.
        2. Hazırlık skorunu hesapla (100 puandan başla, ihlaller için düş).
        3. Emisyon eşik uyarılarını kontrol et.
        4. Son tarih durumunu belirle.
        5. Gerekiyorsa ceza tahmini yap.
        6. ComplianceRiskReport döndür.

        Parametreler
        ------------
        input_payload : InputPayload
            Agent #2'ye gönderilen ham operasyonel veri.
        audit_result : AuditOutput
            AuditorEngine tarafından üretilen denetim çıktısı.

        Döndürür
        --------
        ComplianceRiskReport
        """
        missing_fields = self._find_missing_mandatory_fields(input_payload)
        readiness_score = self._compute_readiness_score(input_payload, audit_result)
        threshold_warnings = self.check_thresholds(audit_result)
        deadline_status = self._evaluate_deadline_status(input_payload.reporting_period)

        is_late = deadline_status == "Overdue"

        estimated_penalty = self.calculate_penalties(
            missing_fields_count=len(missing_fields),
            total_emissions_tco2e=audit_result.emissions.total_emissions,
            readiness_score=readiness_score,
            is_late=is_late,
        )

        supplier_warnings, dirty_supply_cost = self._evaluate_suppliers(
            input_payload, audit_result
        )

        return ComplianceRiskReport(
            readiness_score=readiness_score,
            missing_mandatory_fields=missing_fields,
            estimated_penalty_eur=estimated_penalty,
            threshold_warnings=threshold_warnings,
            deadline_status=deadline_status,
            supplier_benchmark_warnings=supplier_warnings,
            cost_of_dirty_supply_eur=dirty_supply_cost,
        )

    def calculate_penalties(
        self,
        missing_fields_count: int,
        total_emissions_tco2e: float,
        readiness_score: float,
        is_late: bool = False,
    ) -> float:
        """
        Eksik veya geç rapor için tahmini AB CBAM cezasını hesaplar.

        AB CBAM Tüzüğü (2023/956, Madde 26), raporlanmayan veya yanlış
        raporlanan emisyonlar için ton başına €10–€50 arasında ceza öngörür.
        Bu MVP uygulamasında hazırlık skoru eşiğin altında olan veya geç
        gönderilen her rapor için sabit €20/ton uygulanır.

        Parametreler
        ------------
        missing_fields_count : int
            Eksik zorunlu alan sayısı (gelecekteki kademeli ceza mantığı için ayrılmış).
        total_emissions_tco2e : float
            AuditorEngine tarafından hesaplanan toplam emisyon (tCO2e).
        readiness_score : float
            Bu modül tarafından hesaplanan hazırlık skoru.
        is_late : bool
            Raporun resmi son tarihten sonra gönderilip gönderilmediği.

        Döndürür
        --------
        float
            Tahmini ceza miktarı (EUR). Uyumlu ve zamanında ise 0.0.
        """
        if readiness_score < self.readiness_threshold or is_late:
            return round(total_emissions_tco2e * self.penalty_rate, 2)
        return 0.0

    def check_thresholds(self, audit_result: AuditOutput) -> List[str]:
        """
        Emisyon metriklerini AB sektör kıyaslamaları ve
        düzenleyici eşiklerle karşılaştırır.

        Mevcut kontroller
        -----------------
        - Emisyon yoğunluğu (tCO2e/ton çelik) > HIGH_EMISSION_INTENSITY_THRESHOLD
          → AB denetim riski yüksek uyarısı.

        Parametreler
        ------------
        audit_result : AuditOutput
            AuditorEngine tarafından üretilen denetim çıktısı.

        Döndürür
        --------
        List[str]
            İnsan tarafından okunabilir uyarı metinleri. Sorun yoksa boş liste.
        """
        warnings: List[str] = []

        intensity = audit_result.emissions.emission_intensity_per_ton
        if intensity > self.high_intensity_threshold:
            warnings.append(
                f"Yüksek emisyon yoğunluğu tespit edildi: {intensity:.3f} tCO2e/ton "
                f"(eşik: {self.high_intensity_threshold:.1f} tCO2e/ton). "
                "AB denetim riski yüksek. Veri kaynakları doğrulanmalı."
            )

        return warnings

    # ──────────────────────────────────────────────────────────────────────
    # Supplier Benchmarking
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _evaluate_suppliers(
        input_payload: InputPayload,
        audit_result: AuditOutput,
    ) -> tuple[List[str], float]:
        """
        Precursor tedarikçilerini AB kıyaslama faktörleriyle karşılaştırır.

        Her precursor için:
        1. Gerçek emisyon faktörünü belirle (tedarikçi verisi veya CBAM varsayılanı).
        2. AB "İyi Standart" kıyaslama değeri varsa farkı hesapla.
        3. Fark pozitifse ek CBAM maliyetini hesapla.

        Döndürür
        --------
        tuple[List[str], float]
            (uyarı mesajları listesi, toplam kirli tedarik maliyeti EUR)
        """
        warnings: List[str] = []
        total_dirty_cost: float = 0.0

        ets_price = audit_result.financials.ets_price_eur_per_ton
        cbam_factor = audit_result.financials.cbam_phase_factor

        for precursor in input_payload.precursors:
            material_key = precursor.material_name.lower()

            benchmark = EU_BENCHMARK_FACTORS.get(material_key)
            if benchmark is None:
                continue

            actual_factor = (
                precursor.embedded_emissions_factor
                if precursor.embedded_emissions_factor is not None
                else DEFAULT_PRECURSOR_FACTORS.get(material_key, 0.0)
            )

            excess_factor = actual_factor - benchmark
            if excess_factor <= 0:
                continue

            excess_emissions = excess_factor * precursor.quantity_ton
            penalty_eur = round(excess_emissions * ets_price * cbam_factor, 2)

            total_dirty_cost += penalty_eur
            warnings.append(
                f"Supplier for '{precursor.material_name}' is highly carbon-intensive "
                f"(factor: {actual_factor:.2f} vs EU benchmark: {benchmark:.2f}). "
                f"This adds {penalty_eur:,.2f} EUR to your CBAM tax."
            )

        return warnings, round(total_dirty_cost, 2)

    # ──────────────────────────────────────────────────────────────────────
    # Özel Yardımcı Metotlar
    # ──────────────────────────────────────────────────────────────────────

    def _compute_readiness_score(
        self,
        input_payload: InputPayload,
        audit_result: AuditOutput,
    ) -> float:
        """
        Hazırlık skorunu hesaplar: 100 puandan başlayıp ihlaller için düşürür.

        İndirim Kuralları
        -----------------
        1. **−30 puan** — Temel operasyonel veriler (üretim, elektrik, gaz/kömür)
           tamamen sıfır veya boş. Raporun hiçbir temeli yoktur.

        2. **−20 puan** — Proses girdileri (elektrot, kireçtaşı) tamamen eksik.
           Proses emisyonları hesaplanamaz.

        3. **−10 puan** — Her CBAM varsayılan faktörü kullanan precursor başına.
           Tedarikçiden gerçek veri gelmemişse veri kalitesi düşer.

        Skor [0, 100] aralığında kırpılır.
        """
        deductions: float = 0.0

        # ── Kural 1: Temel veriler tamamen eksik ────────────────────────────
        core_is_zero = (
            (input_payload.production_quantity_tons or 0.0) == 0.0
            and (input_payload.electricity_consumption_mwh or 0.0) == 0.0
            and (input_payload.natural_gas_consumption_m3 or 0.0) == 0.0
            and (input_payload.coal_consumption_tons or 0.0) == 0.0
        )
        if core_is_zero:
            deductions += 30.0

        # ── Kural 2: Proses girdileri tamamen eksik ─────────────────────────
        process = input_payload.process_inputs
        process_is_missing = process is None or (
            (process.electrode_consumption_ton or 0.0) == 0.0
            and (process.limestone_consumption_ton or 0.0) == 0.0
        )
        if process_is_missing:
            deductions += 20.0

        # ── Kural 3: CBAM varsayılan faktörü kullanan precursor başına −10 ──
        default_precursor_count = sum(
            1
            for precursor in input_payload.precursors
            if precursor.embedded_emissions_factor is None
        )
        deductions += default_precursor_count * 10.0

        # Skoru [0, 100] aralığında tut ve 2 ondalık yuvarla
        final_score = max(0.0, min(100.0, 100.0 - deductions))
        return round(final_score, 2)

    def _find_missing_mandatory_fields(
        self, input_payload: InputPayload
    ) -> List[str]:
        """
        CBAM raporlaması için zorunlu ancak eksik veya sıfır olan alanları tespit eder.

        Zorunlu Alanlar (AB CBAM Tüzüğü 2023/1773, Ek I gereği)
        ---------------------------------------------------------
        - facility_name           : Tesis adı boş olamaz
        - reporting_period        : Raporlama dönemi belirtilmelidir
        - production_quantity_tons: Üretim > 0 olmalıdır
        - electricity_consumption_mwh : Elektrik tüketimi > 0 olmalıdır
        - yakıt kaynağı            : Doğalgaz, kömür veya önceden hesaplanmış
                                     Scope 1 değerinden en az biri sağlanmalıdır

        Döndürür
        --------
        List[str]
            Eksik alan adlarının listesi.
        """
        missing: List[str] = []

        # Tesis adı
        if not input_payload.facility_name or not input_payload.facility_name.strip():
            missing.append("facility_name")

        # Raporlama dönemi
        if not input_payload.reporting_period:
            missing.append("reporting_period")

        # Üretim miktarı (sıfır üretim raporlanabilir ama şüphelidir)
        if (input_payload.production_quantity_tons or 0.0) <= 0.0:
            missing.append("production_quantity_tons")

        # Elektrik tüketimi
        if (input_payload.electricity_consumption_mwh or 0.0) <= 0.0:
            missing.append("electricity_consumption_mwh")

        # Yakıt kaynağı: doğalgaz, kömür veya önceden hesaplanmış Scope 1
        no_gas = (input_payload.natural_gas_consumption_m3 or 0.0) <= 0.0
        no_coal = (input_payload.coal_consumption_tons or 0.0) <= 0.0
        no_precalculated_scope1 = input_payload.direct_emissions_tco2e is None
        if no_gas and no_coal and no_precalculated_scope1:
            missing.append("fuel_source (natural_gas_m3 | coal_tons | direct_emissions_tco2e)")

        return missing

    def _evaluate_deadline_status(
        self, reporting_period: str
    ) -> Literal["On Time", "At Risk", "Overdue"]:
        """
        Raporlama dönemine göre son tarih durumunu belirler.

        CBAM Raporlama Son Tarihleri (Tüzük 2023/1773, Madde 4)
        ---------------------------------------------------------
        Çeyreklik format ("YYYY-Q#"):
          Q1 (Oca–Mar) → 30 Nisan
          Q2 (Nis–Haz) → 31 Temmuz
          Q3 (Tem–Eyl) → 31 Ekim
          Q4 (Eki–Ara) → 31 Ocak (sonraki yıl)

        Aylık format ("YYYY-MM"):
          Raporlama ayından sonraki ayın son günü.

        Parametreler
        ------------
        reporting_period : str
            Örn: "2026-Q1", "2026-03"

        Döndürür
        --------
        Literal["On Time", "At Risk", "Overdue"]
        """
        deadline = self._parse_deadline(reporting_period)
        if deadline is None:
            # Format tanınmıyorsa yanlış pozitiften kaçınmak için "On Time" dön
            return "On Time"

        today = date.today()
        days_remaining = (deadline - today).days

        if days_remaining < 0:
            return "Overdue"
        if days_remaining <= self.at_risk_days:
            return "At Risk"
        return "On Time"

    @staticmethod
    def _parse_deadline(reporting_period: str) -> Optional[date]:
        """
        Raporlama dönemi metnini çözümleyip resmi başvuru son tarihini döndürür.

        Desteklenen formatlar
        ---------------------
        - "YYYY-Q1" / "YYYY-Q2" / "YYYY-Q3" / "YYYY-Q4"  (Çeyreklik)
        - "YYYY-MM"                                         (Aylık)

        Format tanınmıyorsa None döner.
        """
        period = reporting_period.strip().upper()

        # ── Çeyreklik: "2026-Q1" ────────────────────────────────────────────
        if "-Q" in period:
            try:
                year_str, q_str = period.split("-Q")
                year = int(year_str)
                quarter = int(q_str)
                quarter_deadlines = {
                    1: date(year, 4, 30),
                    2: date(year, 7, 31),
                    3: date(year, 10, 31),
                    4: date(year + 1, 1, 31),
                }
                return quarter_deadlines.get(quarter)
            except (ValueError, KeyError):
                return None

        # ── Aylık: "2026-03" ────────────────────────────────────────────────
        try:
            dt = datetime.strptime(reporting_period[:7], "%Y-%m")
            report_month = dt.month
            report_year = dt.year

            # Son tarih = raporlama ayından bir sonraki ayın son günü
            # Bir sonraki ay hesabı
            if report_month == 12:
                deadline_month_start = date(report_year + 1, 2, 1)
            elif report_month == 11:
                deadline_month_start = date(report_year + 1, 1, 1)
            else:
                deadline_month_start = date(report_year, report_month + 2, 1)

            # Bir önceki gün = bir önceki ayın son günü
            return deadline_month_start - timedelta(days=1)

        except ValueError:
            return None
