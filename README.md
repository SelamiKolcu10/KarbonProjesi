# 🌍 Karbon Salınımı Agentic AI Sistemi

> CBAM (Carbon Border Adjustment Mechanism) belgelerinden otomatik veri çıkarımı, fizik-tabanlı emisyon denetimi, stratejik danışmanlık ve regülatör-uyumlu raporlama yapan çok-ajanlı (multi-agent) AI sistemi.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue?logo=typescript)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📑 İçindekiler

- [Sistem Mimarisi](#-sistem-mimarisi)
- [Ajanlar](#-ajanlar)
- [Frontend](#-frontend-react--typescript)
- [Agent Skills](#-agent-skills-yönetişim-paketi)
- [API](#-api-fastapi)
- [Proje Yapısı](#-proje-yapısı)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Konfigürasyon](#-konfigürasyon)
- [Testler](#-testler)
- [Lisans](#-lisans)

---

## 🏗️ Sistem Mimarisi

```text
                        ┌──────────────────────────────────┐
                        │         React Frontend           │
                        │  (Upload → Job Polling → Report) │
                        └────────────────┬─────────────────┘
                                         │ HTTP / REST
                        ┌────────────────▼─────────────────┐
                        │         FastAPI (src/api.py)      │
                        │  /api/upload  /api/jobs  /api/... │
                        └────────────────┬─────────────────┘
                                         │
                        ┌────────────────▼─────────────────┐
                        │     Orchestrator (Job Lifecycle)  │
                        │  PENDING → RUNNING → COMPLETED    │
                        └──┬──────────┬──────────┬─────────┘
                           │          │          │
               ┌───────────▼──┐  ┌────▼─────┐  ┌▼──────────────┐
               │  Ajan #1     │  │  Ajan #2 │  │  Ajan #3       │
               │  Extractor   │  │  Auditor │  │  Strategist    │
               │  (v3.0)      │  │  (v2.0)  │  │  (Chief + Sim) │
               └──────────────┘  └──────────┘  └───────────────┘
                    PDF/Excel     Emisyon/Mali    Öneri/Senaryo
```

---

## 🤖 Ajanlar

### Ajan #1 — Data Extractor `v3.0`

CBAM mevzuat belgelerini (PDF/Excel) okuyarak yapılandırılmış JSON verisi çıkarır.

| Özellik | Detay |
|---|---|
| PDF işleme | pdfplumber — 53 sayfa/saniye |
| LLM desteği | Gemini veya OpenAI GPT |
| Null-safety | Belgede olmayan veriler `"NULL"` döner, asla uydurma yapılmaz |
| Confidence Score | Çıkarılan her alan için 0.0–1.0 güvenilirlik skoru |
| Batch Processing | Birden fazla PDF tek seferde işlenir |
| Multi-Format Export | CSV / Excel / SQL formatlarında dışa aktarım |
| Document Summary | Otomatik belge özeti |
| Language Detection | 5 dilde otomatik dil tespiti |
| Cache Sistemi | Aynı PDF'i tekrar işlememek için (`<1 saniye`) |
| Retry Mekanizması | API hatalarında 3 kez otomatik tekrar deneme |
| Chunk Processing | Uzun belgeler için parçalı işleme |
| Rate Limiting | API çağrı sınırı kontrolü |
| Progress Callback | Gerçek zamanlı ilerleme bildirimi |

---

### Ajan #2 — Auditor Engine `v2.0`

Çıkarılan verilerden fizik-tabanlı emisyon ve mali uyumluluk denetimi yapar.

| Özellik | Detay |
|---|---|
| Scope 1 & 2 | Doğrudan + elektrik kaynaklı emisyonlar |
| Process Emissions | Elektrot ve kireçtaşı kalsinasyon kimyası |
| Precursor Tracking | Ferro-alaşımlar, hurda çelik, pig-iron gömülü emisyonları |
| Fizik Validasyonu | Enerji yoğunluğu ve imkansızlık kontrolleri |
| Mali Analiz | EU ETS karbon fiyatlaması ile maliyet hesabı |
| CBAM Phase-in | 2026–2034 aşamalı geçiş desteği |
| Confidence Score | AI destekli veri kalitesi değerlendirmesi |
| Anomali Tespiti | Otomatik anormallik işaretleme |
| Audit Trail | Her hesaplama adımı izlenebilir ve regülatöre sunulabilir |

---

### Ajan #3 — Strategist `v1.0`

Denetim sonuçlarını alarak yönetici-odaklı strateji ve senaryo analizi üretir.

**Alt modüller:**

- **`chief_consultant.py`** — Üst düzey strateji önerileri ve aksiyon planı (CAPEX/OPEX/ROI)
- **`compliance_guard.py`** — CBAM uyum durumu ve risk değerlendirmesi
- **`simulator.py`** — Green Shift, Verimlilik, Hurda gibi playbook tabanlı senaryo simülasyonları

---

### Integration Pipeline

```python
# Tek komutla uçtan uca analiz
from src.pipeline import run_analysis

results = run_analysis(
    file_path="factory_invoice.pdf",
    facility_name="ABC Çelik A.Ş.",
    llm_provider="gemini",
    use_cache=True
)
```

Pipeline aşamaları:
1. **Stage 1** — PDF ingestion & extraction (Ajan #1)
2. **Stage 2** — Payload mapping & canonicalization
3. **Stage 2.5** — Data Quality Guard (fail-fast validasyon)
4. **Stage 3** — Emisyon denetimi (Ajan #2)
5. **Stage 4** — Strateji & senaryo analizi (Ajan #3)
6. **Stage 5** — Explainability & audit trail oluşturma

---

### QA — Regression Agent

`src/qa/regression_agent.py` — Emisyon ve vergi hesaplarını golden dataset ile karşılaştırarak CI/CD ortamında doğrulanabilirlik sağlar.

---

## 🖥️ Frontend (React + TypeScript)

Vite tabanlı modern yönetici paneli. Türkçe / İngilizce (i18n) tam destek.

### Sayfalar

| Sayfa | Açıklama |
|---|---|
| `/upload` | PDF/Excel yükleme, Data Quality hata gösterimi (422 kural kodu + aksiyon) |
| `/dashboard` | KPI Cards, Tsunami Chart, Öneri Kartları, Audit Trail |
| `/emission` | Emisyon detay görünümü |
| `/projection` | 5 yıllık CBAM vergi projeksiyonu |
| `/strategy` | Senaryo simülasyon sonuçları |
| `/reports` | Raporlar ve dışa aktarım |
| `/notifications` | Sistem bildirimleri (filtreli) |
| `/settings` | Dil, LLM sağlayıcı ve sistem ayarları |

### Dashboard Bileşenleri

| Bileşen | Açıklama |
|---|---|
| `KPICards.tsx` | Readiness Score, 2026 Tahmini Vergi, Toplam CBAM Emisyonu — risk rengine göre dinamik |
| `TsunamiChart.tsx` | Recharts tabanlı 5 yıllık CBAM vergi artışı bar chart |
| `RecommendationCards.tsx` | Zorluk (Low/Med/High) ve finansal metriklerle stratejik öneri kartları |
| `AuditTrail.tsx` | Regülatöre sunulabilir hesaplama adımları — formül + mevzuat referansı |

### Job Akışı (Frontend ↔ Backend)

```
Upload → POST /api/upload
       → POST /api/jobs/submit
       → useJobPolling hook (PENDING → RUNNING → COMPLETED/FAILED)
       → ExecutiveConsultingReport render (KPI + Chart + Öneriler + Audit)
```

---

## 🧠 Agent Skills Yönetişim Paketi

`.github/skills/` altında 16 skill ile sistemin davranış sözleşmeleri, kalite kapıları ve yönetişim kuralları tanımlanmıştır.

| Skill | Amaç |
|---|---|
| `agent-contract-registry` | Ajan arası JSON/Pydantic kontratların merkezi versiyonlanması |
| `payload-mapping-canonicalization` | Ham JSON → Auditor canonical payload dönüşüm kuralları |
| `carbon-math-governance` | Emisyon faktörleri ve CBAM katsayılarının tek deterministik kaynakta yönetimi |
| `golden-baseline-regression` | Kritik hesaplar için golden dataset karşılaştırması ve fail-fast bloklama |
| `explainability-evidence-composer` | Her sayısal çıktıya zorunlu kanıt paketi (formül + mevzuat + provenance) |
| `data-quality-rule-engine` | Fiziksel imkansızlık ve business rule kontrolleri — rule_id/version bazlı ihlal çıktıları |
| `cbam-regulation-delta-tracker` | AB CBAM mevzuat değişikliklerinin madde bazlı delta takibi |
| `agent-messaging-error-taxonomy` | Çoklu ajan mesajlaşmasında envelope standardı ve hata kodu bazlı tepki sözleşmesi |
| `orchestrator-lifecycle-reliability` | Job lifecycle state machine — idempotent çalışma ve exponential backoff |
| `financial-stress-sensitivity-analyzer` | ETS fiyatı / allocation / phase-in parametrelerinde stres testi matrisi |
| `scenario-simulation-playbook` | Playbook tabanlı senaryo simülasyonları (green shift, efficiency, scrap vb.) |
| `api-contract-consistency-guard` | API kontratları arası çapraz kontrol ve breaking change bloklama |
| `data-provenance-confidence-calibration` | Alan bazlı provenance kaydı, confidence kalibrasyon ve human-in-the-loop kuyruğu |
| `multi-format-ingestion-assurance` | PDF/Excel/CSV/OCR için format-bazlı kalite kapıları ve parser fallback hiyerarşisi |
| `reporting-payload-design-system` | UI'dan bağımsız stabil DTO payload'lar ve zorunlu explainability metadata |
| `architecture-guardian-scaffolding` | Yeni ajan/modül eklemelerinde zorunlu compliance checklist ve governance gate |

---

## ⚡ API (FastAPI)

`src/api.py` — Çalıştırma: `python src/api.py`

### Temel Endpoint'ler

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/api/upload` | PDF/Excel dosyası yükle |
| `POST` | `/api/validate-payload` | Payload doğrula (Data Quality Guard) |
| `POST` | `/api/jobs/submit` | Analiz işi başlat |
| `GET` | `/api/jobs/{job_id}` | İş durumu sorgula (`PENDING/RUNNING/COMPLETED/FAILED/REJECTED_BY_GUARD`) |
| `GET` | `/api/jobs/{job_id}/result` | Tamamlanan iş sonucunu getir |
| `GET` | `/api/health` | Sistem sağlık kontrolü |

### Hata Modeli

Data Quality ihlallerinde `422` yanıtı kural kodlu ve yapısal döner:

```json
{
  "detail": [
    {
      "rule_id": "PHYS_001",
      "rule_version": "1.0",
      "description": "Enerji yoğunluğu fiziksel sınırı aşıyor",
      "action": "Elektrik tüketimini üretim miktarıyla orantılı girin"
    }
  ]
}
```

---

## 📁 Proje Yapısı

```text
KarbonSalınımProjesi/
│
├── src/                              # Backend çekirdeği
│   ├── agents/
│   │   ├── data_extractor.py         # Ajan #1 — PDF/Excel veri çıkarımı (v3.0)
│   │   ├── auditor/                  # Ajan #2 — Emisyon denetimi (v2.0)
│   │   │   ├── logic.py              #   Ana denetim mantığı
│   │   │   ├── models.py             #   Pydantic veri modelleri
│   │   │   ├── physics.py            #   Fizik-tabanlı validasyon
│   │   │   ├── constants.py          #   Emisyon faktörleri ve sabitler
│   │   │   └── logger.py             #   Audit-trail logger
│   │   ├── strategist/               # Ajan #3 — Strateji ve senaryo
│   │   │   ├── chief_consultant.py   #   Yönetici danışmanlık raporu
│   │   │   ├── compliance_guard.py   #   CBAM uyum değerlendirmesi
│   │   │   └── simulator.py          #   Senaryo simülasyonu
│   │   ├── explainability/
│   │   │   └── explainer.py          #   XAI açıklama üretici
│   │   └── guards/
│   │       └── schema_guard.py       #   Data Quality Guard (fail-fast)
│   ├── orchestration/
│   │   └── orchestrator.py           #   Job lifecycle yönetimi
│   ├── api/
│   │   └── main.py                   #   FastAPI modüler router
│   ├── qa/
│   │   └── regression_agent.py       #   Regression & golden baseline QA
│   ├── utils/
│   │   ├── cache.py                  #   PDF önbelleği
│   │   ├── export.py                 #   CSV/Excel/SQL dışa aktarım
│   │   ├── language.py               #   Dil tespiti
│   │   ├── logger.py                 #   Merkezi loglama
│   │   ├── retry.py                  #   Retry mekanizması
│   │   ├── statistics.py             #   İşlem istatistikleri
│   │   └── validators.py             #   Girdi validasyonu
│   ├── api.py                        #   FastAPI ana uygulama
│   ├── pipeline.py                   #   Uçtan uca analiz pipeline
│   └── config.py                     #   Merkezi konfigürasyon
│
├── frontend/                         # React + TypeScript yönetici paneli
│   ├── src/
│   │   ├── pages/
│   │   │   ├── upload/               #   Dosya yükleme + Data Quality feedback
│   │   │   ├── dashboard/            #   Ana yönetici panosu
│   │   │   ├── emission/             #   Emisyon detayı
│   │   │   ├── projection/           #   5 yıllık projeksiyon
│   │   │   ├── strategy/             #   Senaryo sonuçları
│   │   │   ├── reports/              #   Raporlar
│   │   │   ├── notifications/        #   Bildirimler
│   │   │   └── settings/             #   Ayarlar
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICards.tsx      #   Risk-rengi dinamik KPI kartları
│   │   │   │   ├── TsunamiChart.tsx  #   5 yıllık CBAM vergi bar chart
│   │   │   │   ├── RecommendationCards.tsx  # Stratejik öneri kartları
│   │   │   │   └── AuditTrail.tsx    #   Regülatör-uyumlu hesaplama izi
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx     #   Ana sayfa düzeni
│   │   │   │   ├── Sidebar.tsx       #   Gezinti çubuğu
│   │   │   │   └── TopBar.tsx        #   Üst çubuk (dil seçici)
│   │   │   └── ui/                   #   Ortak UI bileşenleri (Button, Card…)
│   │   ├── hooks/
│   │   │   └── useJobPolling.ts      #   Job durumu reaktif polling hook
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts         #   Merkezi HTTP istemcisi
│   │   │   │   ├── jobs.ts           #   Job API servisi
│   │   │   │   └── types.ts          #   API tip tanımları
│   │   │   ├── i18n.ts               #   TR/EN çeviri altyapısı
│   │   │   ├── formatters.ts         #   Locale-aware sayı/para formatlama
│   │   │   └── utils.ts              #   Genel yardımcılar
│   │   └── locales/
│   │       ├── tr.json               #   Türkçe çeviriler
│   │       └── en.json               #   İngilizce çeviriler
│   └── vite.config.ts
│
├── .github/
│   └── skills/                       # 16 Agent Skills (yönetişim paketi)
│       ├── agent-contract-registry/
│       ├── carbon-math-governance/
│       ├── cbam-regulation-delta-tracker/
│       └── ... (13 skill daha)
│
├── tests/                            # Test paketi
│   ├── test_api_orchestrator.py
│   ├── test_auditor.py
│   ├── test_data_extractor.py
│   ├── test_orchestrator.py
│   ├── test_v2_upgrade.py
│   └── test_v3.py
│
├── examples/                         # Örnek kullanım scriptleri
│   ├── run_data_extractor.py
│   ├── demo_v3_features.py
│   └── simple_usage.py
│
├── scripts/                          # Yardımcı scriptler
│   ├── python/                       #   Python yardımcıları
│   └── js/                           #   JS yardımcıları
│
├── bin/                              # Windows .bat çalıştırıcılar
├── mevzuat_docs/                     # CBAM mevzuat PDF'leri
├── docs/                             # Dokümantasyon
│   ├── AJANLAR.md
│   ├── CHANGELOG.md
│   └── KURULUM.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- Node.js 18+
- Gemini API Key **veya** OpenAI API Key

### 1 — Python bağımlılıkları

```bash
pip install -r requirements.txt
```

### 2 — Ortam değişkenleri

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
GEMINI_API_KEY=your_gemini_api_key
# VEYA
OPENAI_API_KEY=your_openai_api_key

DEFAULT_LLM_PROVIDER=gemini
```

### 3 — Frontend bağımlılıkları

```bash
cd frontend
npm install
npm run dev
```

### 4 — Backend API'yi başlat

```bash
python src/api.py
```

---

## 💡 Kullanım

### Ajan #1 — Data Extractor

```python
from src.agents.data_extractor import DataExtractor

extractor = DataExtractor(llm_provider="gemini")
result = extractor.process_document(
    pdf_path="mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf",
    output_path="output/extracted_data.json"
)

print(result['document_name'])       # "Regulation (EU) 2023/956"
print(result['confidence_score'])    # 0.92
```

### Ajan #2 — Auditor Engine

```python
from src.agents.auditor import AuditorEngine
from src.agents.auditor.models import InputPayload

auditor = AuditorEngine(
    strict_physics=False,
    cbam_phase_factor=0.025,   # 2026: %2.5 phase-in
    free_allocation=0.0
)

payload = InputPayload(
    facility_name="ABC Döküm Sanayi",
    reporting_period="2026-03",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0
)

result = auditor.audit(payload)
print(f"Toplam Emisyon : {result.emissions.total_emissions:.2f} tCO2e")
print(f"Mali Yükümlülük: €{result.financials.effective_liability_eur:,.2f}")
print(f"Uyum Durumu    : {result.is_compliant}")
```

### Uçtan Uca Pipeline

```python
from src.pipeline import run_analysis

results = run_analysis(
    file_path="factory_invoice.pdf",
    facility_name="ABC Çelik A.Ş.",
    llm_provider="gemini",
    use_cache=True
)

print(f"Toplam Emisyon : {results['summary']['total_emissions_tco2e']:.2f} tCO2e")
print(f"Mali Yükümlülük: €{results['summary']['financial_liability_eur']:,.2f}")
print(f"Durum          : {results['summary']['compliance_status']}")
```

**CLI:**

```bash
python -m src.pipeline document.pdf --facility-name "ABC Çelik"
```

---

## 📊 Çıktı Şeması (Data Extractor)

```json
{
  "document_name": "Regulation (EU) 2023/956",
  "document_number": "32023R0956",
  "document_type": "regulation",
  "publication_date": "2023-05-16",
  "effective_date": "2023-06-05",
  "issuing_authority": "European Parliament and Council",
  "sectors_covered": ["Cement", "Iron and steel", "Aluminium", "Fertilisers", "Electricity"],
  "compliance_deadlines": [
    { "date": "2026-01-01", "description": "Full CBAM reporting obligation begins" }
  ],
  "confidence_score": 0.94,
  "_metadata": {
    "source_file": "CELEX_32023R0956_EN_TXT.pdf",
    "extraction_date": "2026-06-05 14:30:00",
    "llm_provider": "gemini",
    "text_length": 125847,
    "language": "en"
  }
}
```

> **Not:** Belgede bulunmayan alanlar `"NULL"` döner. Sistem asla bilgi uydurmaz.

---

## 🔧 Konfigürasyon

`src/config.py`:

```python
DEFAULT_LLM_PROVIDER = "gemini"   # "gemini" veya "gpt"
LLM_TEMPERATURE      = 0.1        # Düşük = tutarlı çıktı
LLM_MAX_TOKENS       = 4096
MAX_TEXT_LENGTH      = 15000      # LLM'e gönderilecek max karakter
CACHE_ENABLED        = True
RETRY_COUNT          = 3
```

---

## 🧪 Testler

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Belirli test dosyası
pytest tests/test_auditor.py -v
pytest tests/test_api_orchestrator.py -v
```

Test kapsamı:
- `test_api_orchestrator.py` — Job submit/process/status akışları
- `test_auditor.py` — Emisyon ve mali hesaplama doğruluğu
- `test_data_extractor.py` — PDF çıkarım testleri
- `test_orchestrator.py` — Orchestrator lifecycle
- `test_v2_upgrade.py` — v2.0 geriye uyumluluk
- `test_v3.py` — v3.0 özellik testleri

---

## ✅ Tamamlanan Bileşenler

- [x] **Ajan #1: Data Extractor** (v3.0) — PDF/Excel veri çıkarımı
- [x] **Ajan #2: Auditor Engine** (v2.0) — CBAM emisyon ve mali denetim
- [x] **Ajan #3: Strategist** (v1.0) — Yönetici danışmanlık + senaryo simülasyonu
- [x] **Integration Pipeline** — Uçtan uca 5 aşamalı analiz akışı
- [x] **Data Quality Guard** — Fail-fast validasyon katmanı
- [x] **Orchestrator** — Asenkron job lifecycle yönetimi
- [x] **Explainability Agent** — XAI + audit trail
- [x] **Regression QA Agent** — Golden baseline doğrulaması
- [x] **FastAPI Backend** — REST API + 422 kural kodlu hata modeli
- [x] **React Frontend** — Upload → Polling → Executive Report akışı
- [x] **i18n** — Türkçe / İngilizce tam destek
- [x] **16 Agent Skills** — Yönetişim, kalite ve sözleşme paketi

## 🔜 Planlanan Bileşenler

- [ ] **Ajan #4: Report Generator** — PDF/Excel resmi rapor oluşturma
- [ ] **Ajan #5: Document Classifier** — Belge tipi sınıflandırma
- [ ] **Ajan #6: Regulation Monitor** — AB CBAM mevzuat değişikliklerini otomatik takip

---

## 📚 Dokümantasyon

| Dosya | İçerik |
|---|---|
| [AJANLAR.md](docs/AJANLAR.md) | Her ajanın teknik detayları |
| [CHANGELOG.md](docs/CHANGELOG.md) | Sürüm geçmişi ve değişiklik listesi |
| [KURULUM.md](docs/KURULUM.md) | Detaylı kurulum kılavuzu |
| [PROJE_KONTROL.md](PROJE_KONTROL.md) | Güncel durum notları ve kontrol listesi |

---

## 📄 Lisans

MIT License — Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için lütfen önce issue açın.

---

> **Önemli Not:** Bu sistem CBAM mevzuatı analizi ve uyumluluk değerlendirmesi için geliştirilmiştir. Gerçek uygulamalarda çıktılar yetkili bir uzman tarafından doğrulanmalıdır.
