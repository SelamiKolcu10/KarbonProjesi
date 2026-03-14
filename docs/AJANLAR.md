# 🤖 CBAM Agentic AI Sistemi - Ajanlar Rehberi

Bu dokümanda sistemdeki tüm ajanların görevleri, yetenekleri ve kullanımları detaylı şekilde açıklanmaktadır.

---

## 📋 Sistem Mimarisi

```text
┌─────────────────────────────────────────────────────────────────┐
│                    CBAM Uyumluluk Sistemi                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌──────────────────────┐
│   AJAN #1         │                    │   AJAN #2            │
│ Data Extractor    │ ─────JSON────────> │ Auditor Engine       │
│    (v3.0)         │                    │    (v2.0)            │
└───────────────────┘                    └──────────────────────┘
        │                                           │
        │                                           │
        ▼                                           ▼
   PDF Belgeler                              Audit Raporları
   Yapılandırılmış                           Mali Tahminler
        Veri                                 Emisyon Hesaplamaları
```

---

## 📄 AJAN #1: DATA EXTRACTOR (Belge Veri Çıkarıcı)

### 🎯 Temel Bilgiler

- **Versiyon**: v3.0 (Full-Featured)
- **Dosya**: `src/agents/data_extractor.py`
- **Görev**: PDF belgelerinden yapılandırılmış veri çıkarma
- **AI Kullanımı**: ✅ Gemini 2.5 Flash / GPT-4o
- **Hız**: ~53 sayfa/saniye

### 🔧 Ana Görevleri

#### 1. PDF İşleme ve Okuma

```python
# PDF'den metin çıkarma
text = extractor.extract_text_from_pdf("belge.pdf")

# Metadata çıkarma
metadata = extractor.extract_pdf_metadata("belge.pdf")
# → {"title": "...", "author": "...", "page_count": 53}
```

**Özellikler**:

- pdfplumber kütüphanesi ile sayfa sayfa okuma
- Otomatik metin temizleme ve normalizasyon
- PDF metadata çıkarma (başlık, yazar, tarih, sayfa sayısı)
- Boş sayfa kontrolü
- Hata yönetimi

#### 2. LLM ile Yapılandırılmış Veri Çıkarma

**Desteklenen AI Modelleri**:

| Model | Provider | Hız | Maliyet | Kalite |
| --- | --- | --- | --- | --- |
| Gemini 2.5 Flash | Google | Çok Hızlı | Düşük | Yüksek |
| GPT-4o | OpenAI | Hızlı | Orta | Çok Yüksek |

**Çıkarılan Veri Şeması**:

```json
{
  "document_name": "string or NULL",
  "document_number": "string or NULL",
  "document_type": "Regulation/Directive/Decision",
  "publication_date": "YYYY-MM-DD or NULL",
  "effective_date": "YYYY-MM-DD or NULL",
  "issuing_authority": "European Commission/...",
  "legal_basis": "Treaty Article/...",
  "scope": "Sectors and coverage description",
  "sectors_covered": ["Iron & Steel", "Cement", "..."],
  "emissions_categories": ["Scope 1", "Scope 2", "Scope 3"],
  "key_obligations": [
    "Obligation 1",
    "Obligation 2"
  ],
  "reporting_requirements": "Description of reporting needs",
  "compliance_deadlines": [
    {
      "date": "2026-12-31",
      "description": "First CBAM report"
    }
  ],
  "penalties": "Penalty descriptions",
  "relevant_articles": ["Article 5", "Article 10"],
  "_metadata": {
    "source_file": "document.pdf",
    "extraction_date": "2026-03-06 14:30:00",
    "llm_provider": "gemini",
    "text_length": 45678,
    "page_count": 53,
    "processing_time_seconds": 8.5
  }
}
```

#### 3. NULL Değer Yönetimi

**Önemli Prensip**: Sistem ASLA bilgi uydurmaz!

```json
{
  "document_name": "Regulation (EU) 2023/956",  // ✅ Belgede var
  "publication_date": "2023-05-16",              // ✅ Belgede var
  "some_field_not_in_document": "NULL"           // ⚠️ Belgede yok
}
```

Eğer bir bilgi **açıkça belirtilmemişse**, o alan `"NULL"` değeri döner.

### ⭐ v3.0 - Yeni Özellikler (6 Büyük Ekleme)

#### 1️⃣ Batch Processing (Toplu İşleme)

Birden fazla PDF'i tek seferde işleme yeteneği:

```python
from src.agents.data_extractor import DataExtractor

extractor = DataExtractor()

# Toplu işleme
results = extractor.process_batch(
    pdf_paths=[
        "belge1.pdf",
        "belge2.pdf",
        "belge3.pdf",
        "belge4.pdf"
    ],
    output_dir="output/batch_results"
)

# Sonuçlar
print(f"Başarılı: {results['successful']}")
print(f"Başarısız: {results['failed']}")
```

**Avantajlar**:

- Tek komutla çoklu PDF işleme
- Paralel işleme desteği (opsiyonel)
- Hata durumunda diğer dosyalar işlenmeye devam eder
- Toplu export (CSV, Excel)

#### 2️⃣ Confidence Score (Güven Skoru)

Çıkarılan verinin kalitesini 0.0-1.0 arasında puanlar:

```python
result = extractor.process_document("belge.pdf")

print(f"Güven Skoru: {result['_metadata']['confidence_score']}")
# → 0.95 (Yüksek kalite)
# → 0.65 (Orta kalite, bazı alanlar eksik)
# → 0.40 (Düşük kalite, çok fazla NULL)
```

**Hesaplama Kriterleri**:

- NULL değer oranı (%)
- Metin kalitesi
- Tarih formatı doğruluğu
- Liste öğesi sayısı
- Metadata tamlığı

#### 3️⃣ Multi-Format Export

Farklı formatlarda veri dışa aktarma:

**CSV Export**:

```python
from src.utils.export import export_to_csv

export_to_csv(result, "output/data.csv")
```

**Excel Export**:

```python
from src.utils.export import export_to_excel

# Tek doküman
export_to_excel(result, "output/data.xlsx")

# Batch results
export_batch_to_excel(results, "output/all_documents.xlsx")
```

**SQL Export**:

```python
from src.utils.export import export_to_sql_inserts

sql_statements = export_to_sql_inserts(
    result, 
    table_name="cbam_documents"
)
# → INSERT INTO cbam_documents (document_name, ...) VALUES (...);
```

#### 4️⃣ Document Summary (Belge Özeti)

Belgenin otomatik özetini oluşturur:

```python
result = extractor.process_document(
    "belge.pdf",
    include_summary=True
)

print(result['_metadata']['summary'])
# → "This regulation establishes the CBAM framework for 
#    iron & steel sector, requiring quarterly reporting 
#    starting from Q4 2023..."
```

**Özet Özellikleri**:

- 100-200 kelime arası
- Anahtar noktaları vurgular
- Tarihler ve sayılar içerir
- Sektör ve kapsam bilgisi

#### 5️⃣ Language Detection (Dil Tespiti)

Otomatik dil tespiti ve analizi:

```python
from src.utils.language import detect_language, detect_language_advanced

# Basit tespit
lang = detect_language(text)
# → "en" (İngilizce)

# Gelişmiş tespit
lang_info = detect_language_advanced(text)
# → {
#     "language": "en",
#     "confidence": 0.98,
#     "alternatives": [
#         {"language": "de", "confidence": 0.02}
#     ]
# }
```

**Desteklenen Diller**:

- 🇹🇷 Türkçe (TR)
- 🇬🇧 İngilizce (EN)
- 🇫🇷 Fransızca (FR)
- 🇩🇪 Almanca (DE)
- 🇪🇸 İspanyolca (ES)

#### 6️⃣ Statistics & Reporting (İstatistikler)

Detaylı işlem istatistikleri:

```python
from src.utils.statistics import ProcessingStats

stats = ProcessingStats()

# İşlemden sonra
summary = stats.get_summary()

print(summary)
# → {
#     "total_documents": 10,
#     "successful": 9,
#     "failed": 1,
#     "total_pages": 453,
#     "total_text_length": 1250000,
#     "total_time_seconds": 85.3,
#     "average_time_per_document": 8.53,
#     "average_pages_per_document": 45.3,
#     "cache_hits": 3,
#     "cache_hit_rate": 0.30,
#     "llm_provider": "gemini"
# }
```

### ✨ v2.0 Özellikleri

#### Retry Mekanizması

API hatalarında otomatik tekrar deneme:

```python
@retry_with_backoff(max_retries=3, base_delay=1.0)
def call_llm():
    # API çağrısı yapar
    # Hata olursa 3 kez tekrar dener
    # Bekleme süreleri: 1s, 2s, 4s (exponential backoff)
```

#### Cache Sistemi

Aynı PDF'i tekrar işlemez:

```python
# İlk çalıştırma: 8.5 saniye
result1 = extractor.process_document("belge.pdf")

# İkinci çalıştırma: <1 saniye (cache'den gelir!)
result2 = extractor.process_document("belge.pdf")
```

**Cache Özellikleri**:

- SHA-256 hash ile dosya takibi
- TTL (Time To Live) desteği (varsayılan: 24 saat)
- `cache/` klasöründe JSON olarak saklanır
- Manuel cache temizleme mümkün

#### Chunk Processing

Uzun belgeler için parçalı işleme:

```python
# 15.000 karakter bloklar halinde işler
# Her chunk ayrı ayrı LLM'e gönderilir
# Sonuçlar birleştirilir
```

**Avantajlar**:

- Token limiti aşımını önler
- Daha iyi performans
- Daha az hata

#### Rate Limiting

API çağrı limiti kontrolü:

```python
extractor = DataExtractor(
    rate_limit_per_minute=10  # Dakikada max 10 çağrı
)
```

#### Progress Tracking

Gerçek zamanlı ilerleme bildirimi:

```python
def progress_callback(stage, current, total):
    print(f"{stage}: {current}/{total}")

extractor.process_document(
    "belge.pdf",
    progress_callback=progress_callback
)
# → extract_text: 10/53
# → extract_text: 20/53
# → ...
```

#### Detaylı Loglama

Her adım `logs/` klasöründe kaydedilir:

```text
logs/data_extractor_2026-03-06.log
```

```log
2026-03-06 14:30:15 - INFO - PDF okunuyor: belge.pdf
2026-03-06 14:30:18 - INFO - PDF okuma tamamlandı: 53 sayfa
2026-03-06 14:30:19 - INFO - LLM çağrısı yapılıyor...
2026-03-06 14:30:23 - INFO - JSON parse başarılı
2026-03-06 14:30:23 - INFO - İşlem tamamlandı: 8.5 saniye
```

### 📊 Data Extractor Kullanım Örnekleri

#### Temel Extractor Kullanımı

```python
from src.agents.data_extractor import DataExtractor

# Extractor oluştur
extractor = DataExtractor(llm_provider="gemini")

# PDF işle
result = extractor.process_document(
    pdf_path="mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf",
    output_path="output/extracted_data.json"
)

# Sonuçları kullan
print("Belge:", result['document_name'])
print("Yayın Tarihi:", result['publication_date'])
print("Sektörler:", result['sectors_covered'])
```

#### Gelişmiş Kullanım (v3.0)

```python
from src.agents.data_extractor import DataExtractor
from src.utils.export import export_to_excel

# Gelişmiş konfigürasyon
extractor = DataExtractor(
    llm_provider="gemini",
    use_cache=True,
    cache_ttl_hours=24,
    max_retries=3,
    chunk_size=15000,
    rate_limit_per_minute=10,
    enable_stats=True
)

# Batch processing
results = extractor.process_batch(
    pdf_paths=[
        "belge1.pdf",
        "belge2.pdf",
        "belge3.pdf"
    ],
    output_dir="output/batch",
    include_summary=True
)

# Excel export
export_to_excel(results, "output/all_documents.xlsx")

# İstatistikleri görüntüle
stats = extractor.stats.get_summary()
print(f"Toplam süre: {stats['total_time_seconds']:.2f}s")
print(f"Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
```

---

## 🧮 AJAN #2: AUDITOR ENGINE (Denetim ve Hesaplama Motoru)

### 🎯 Ana Bilgiler

- **Versiyon**: v2.0 (Chemistry & Precursors Enabled)
- **Dosya**: `src/agents/auditor/`
- **Görev**: Emisyon hesaplama ve CBAM mali tahmin
- **AI Kullanımı**: ❌ (Deterministik matematiksel hesaplamalar)
- **Hız**: Anlık (<1 saniye)

### 🔧 Anahtar İşlevler

#### 1. Fizik Bazlı Validasyon

Girilen verinin fiziksel olarak mümkün olup olmadığını kontrol eder.

**Enerji Yoğunluğu Kontrolleri**:

```python
# Çelik üretimi için gerçekçi aralıklar
STEEL_MIN_ENERGY_PER_TON = 0.2  # MWh/ton (200 kWh/ton)
STEEL_TYPICAL_ENERGY_PER_TON = 0.4  # MWh/ton (400 kWh/ton)
STEEL_MAX_ENERGY_PER_TON = 0.7  # MWh/ton (700 kWh/ton)

# Kontrol
energy_intensity = electricity_mwh / production_tons

if energy_intensity < 0.2:
    → CRITICAL: "Fiziksel olarak imkansız (çok düşük)"
elif energy_intensity > 0.7:
    → WARNING: "Çok yüksek enerji tüketimi"
```

**Anomali Seviyeleri**:

| Seviye | Açıklama | Uyumluluk |
| --- | --- | --- |
| INFO | Bilgilendirme | Uyumlu |
| WARNING | Uyarı, kontrol et | Kontrol gerekli |
| CRITICAL | Kritik hata | Uyumsuz |

**Kontrol Edilen Durumlar**:

```python
# 1. Sıfır üretim tuzağı
if production == 0 and (electricity > 10 or gas > 1000):
    → WARNING: "Üretim yok ama enerji tüketimi var"

# 2. Emisyon yoğunluğu
emission_intensity = total_emissions / production
if emission_intensity > 2.5:
    → WARNING: "Çok yüksek emisyon yoğunluğu"

# 3. Enerji-emisyon tutarlılığı
# Otomatik çapraz kontroller
```

#### 2. Scope 1 & 2 Emisyon Hesaplamaları

**SCOPE 1 (Doğrudan Emisyonlar)**:

Tesiste yakılan yakıtlardan kaynaklanan emisyonlar.

```python
# Doğalgaz
NATURAL_GAS_FACTOR = 0.00212  # tCO2/m³
natural_gas_emissions = m³ × 0.00212

# Kömür
COAL_FACTOR = 2.42  # tCO2/ton
coal_emissions = ton × 2.42

# Toplam Scope 1
scope_1_total = natural_gas_emissions + coal_emissions
```

**SCOPE 2 (Dolaylı Emisyonlar)**:

Satın alınan elektrikten kaynaklanan emisyonlar.

```python
# Türkiye şebekesi faktörü
GRID_FACTOR_TURKEY = 0.43  # tCO2e/MWh

electricity_emissions = MWh × 0.43

# AB ortalaması (karşılaştırma için)
GRID_FACTOR_EU = 0.275  # tCO2e/MWh
```

#### 3. ⭐ v2.0 - Process Emissions (Proses Emisyonları)

Kimyasal reaksiyonlardan kaynaklanan emisyonlar.

**Elektrot Oksidasyonu** (Electric Arc Furnace):

```text
Kimya: C + O₂ → CO₂

Moleküler ağırlıklar:
- C (Karbon): 12
- CO₂ (Karbondioksit): 44

Dönüşüm faktörü: 44/12 = 3.664 tCO₂/ton elektrot
```

```python
ELECTRODE_CO2_FACTOR = 3.664  # tCO2/ton

electrode_emissions = electrode_consumption_ton × 3.664
```

**Kireçtaşı Kalsinasyonu** (Flux Material):

```text
Kimya: CaCO₃ → CaO + CO₂

CaCO₃ (Kalsiyum karbonat) → CaO (Kireç) + CO₂
Her ton CaCO₃'ten ~0.44 ton CO₂ açığa çıkar
```

```python
LIMESTONE_CO2_FACTOR = 0.44  # tCO2/ton

limestone_emissions = limestone_consumption_ton × 0.44
```

**Örnek Hesaplama**:

```python
# Girdi
process_inputs = ProcessInputs(
    electrode_consumption_ton=2.5,
    limestone_consumption_ton=10.0
)

# Hesaplama
electrode_emissions = 2.5 × 3.664 = 9.16 tCO2e
limestone_emissions = 10.0 × 0.44 = 4.40 tCO2e

total_process_emissions = 9.16 + 4.40 = 13.56 tCO2e
```

#### 4. ⭐ v2.0 - Precursor Emissions (Hammadde Gömülü Emisyonları)

Çelik üretiminde kullanılan alaşım ve hammaddelerin gömülü (embedded) emisyonları.

**Desteklenen Precursor Malzemeler**:

| Malzeme | Emisyon Faktörü (tCO₂e/ton) | Açıklama |
| --- | --- | --- |
| ferro-manganese | 1.65 | Manganez alaşımı |
| ferro-silicon | 2.10 | Silikon alaşımı |
| ferro-chromium | 2.85 | Krom alaşımı |
| ferro-nickel | 3.20 | Nikel alaşımı |
| silicon-manganese | 1.95 | Si-Mn alaşımı |
| scrap-steel | 0.35 | Hurda çelik (geri dönüşüm) |
| pig-iron | 2.30 | Pik demir |
| dri | 1.80 | Direct Reduced Iron |
| hbi | 1.85 | Hot Briquetted Iron |
| lime | 0.75 | Kireç |

**Akıllı Faktör Yönetimi**:

Sistem iki şekilde çalışır:

**1. Gerçek Tedarikçi Verisi** (Tercih edilir):

```python
precursor = PrecursorInput(
    material_name="ferro-manganese",
    quantity_ton=5.0,
    embedded_emissions_factor=1.65  # ✅ Tedarikçiden gelen gerçek veri
)
# Güven skorunu etkilemez
```

**2. CBAM Varsayılan Değeri** (Fallback):

```python
precursor = PrecursorInput(
    material_name="ferro-silicon",
    quantity_ton=3.0,
    embedded_emissions_factor=None  # ⚠️ Default kullanılacak
)
# Sistem 2.10 tCO2e/ton kullanır (CBAM default)
# Güven skorunu düşürür (-10%)
```

**Hesaplama Örneği**:

```python
# 3 farklı precursor
precursors = [
    PrecursorInput("ferro-manganese", 5.0, 1.65),    # Gerçek veri
    PrecursorInput("ferro-silicon", 3.0, None),      # Default
    PrecursorInput("scrap-steel", 450.0, 0.35)       # Gerçek veri
]

# Hesaplama
emissions = [
    5.0 × 1.65 = 8.25 tCO2e,
    3.0 × 2.10 = 6.30 tCO2e,  # Default kullanıldı
    450.0 × 0.35 = 157.50 tCO2e
]

total_precursor_emissions = 172.05 tCO2e
```

#### 5. ⭐ v2.0 - Confidence Scoring (Güven Skoru)

Veri kalitesini otomatik değerlendirir.

**Skorlama Algoritması**:

```python
# Başlangıç
confidence = 1.0  # 100%

# Deduction 1: Precursor default factors
if using_defaults:
    deduction = 0.1 × (num_defaults / total_precursors)
    confidence -= deduction

# Deduction 2: Missing process inputs
if not has_process_inputs:
    confidence -= 0.2

# Minimum skor
confidence = max(0.5, confidence)
```

**Örnekler**:

| Durum | Hesaplama | Skor |
| --- | --- | --- |
| Tam veri (her şey gerçek) | 1.0 | 100% |
| 3 precursor, 1'i default | 1.0 - 0.1×(1/3) = 0.97 | 97% |
| Process yok, 1 default | 1.0 - 0.2 - 0.1×(1/3) = 0.77 | 77% |
| Process yok, tüm default | 1.0 - 0.2 - 0.1 = 0.7 | 70% |
| Sadece yakıt verisi | 1.0 - 0.2 = 0.8 | 80% |

#### 6. Mali Etki Analizi

CBAM kapsamında mali yükümlülüğü hesaplar.

**Formüller**:

```python
# 1. Net yükümlülük
net_liable_emissions = total_emissions - free_allocation

# 2. Toplam vergi (tam fiyat)
total_liability = net_liable_emissions × ETS_price
# ETS_price = €85/ton CO2 (2026 fiyatı)

# 3. CBAM fazlı geçiş (2026-2034)
CBAM_PHASE_2026 = 0.025  # %2.5
CBAM_PHASE_2027 = 0.05   # %5
CBAM_PHASE_2030 = 0.80   # %80
CBAM_PHASE_2034 = 1.00   # %100

effective_liability = total_liability × cbam_phase_factor

# 4. Ton çelik başına maliyet
cost_per_ton_steel = effective_liability / production_tons
```

**Örnek Hesaplama** (2026):

```python
# Girdi
total_emissions = 303.42 tCO2e
free_allocation = 0.0 tCO2e  # Worst-case
production = 500 ton
ETS_price = €85/ton

# Hesaplama
net_liable = 303.42 - 0.0 = 303.42 tCO2e
total_liability = 303.42 × €85 = €25,790.59
effective_liability = €25,790.59 × 0.025 = €644.76  # 2026 fazı
cost_per_ton = €644.76 / 500 = €1.29/ton çelik
```

#### 7. Audit Trail (Denetim İzi)

Her hesaplama adımını şeffaf şekilde kaydeder.

**Örnek Audit Trail**:

```text
CBAM Audit Trail - ABC Döküm Sanayi (2026-03)
================================================================

Step 1 [VALIDATION]
Description: Physics validation passed
Result: ✅ PASSED - All inputs within plausible ranges
Source: Physics-based sanity check

Step 2 [SCOPE1]
Description: Scope 1 emissions from Natural Gas
Formula: 15000.00 m³ × 0.0021 tCO2/m³ = 31.8087 tCO2e
Result: 31.8087 tCO2e
Source: IPCC (2006) Guidelines for National GHG Inventories

Step 3 [SCOPE1]
Description: Total Scope 1 (Direct) Emissions
Formula: 31.8087 (gas) + 0.0000 (coal) = 31.8087
Result: 31.8087 tCO2e
Source: Regulation (EU) 2023/1773 - CBAM Implementation

Step 4 [SCOPE2]
Description: Scope 2 emissions from electricity (Turkey grid)
Formula: 200.00 MWh × 0.4300 tCO2e/MWh = 86.0000 tCO2e
Result: 86.0000 tCO2e
Source: Regulation (EU) 2023/1773, Annex IV

Step 5 [PROCESS]
Description: Electrode consumption (C → CO₂)
Formula: 2.5000 ton × 3.6640 = 9.1600 tCO2e
Result: 9.1600 tCO2e
Source: Regulation (EU) 2023/1773, Annex I (Iron & Steel)

Step 6 [PROCESS]
Description: Limestone calcination (CaCO₃ → CaO + CO₂)
Formula: 10.0000 ton × 0.4400 = 4.4000 tCO2e
Result: 4.4000 tCO2e
Source: IPCC (2006), Volume 3

Step 7 [PRECURSOR]
Description: Precursor: ferro-manganese (Supplier Actual)
Formula: 5.0000 ton × 1.6500 tCO2e/ton = 8.2500 tCO2e
Result: 8.2500 tCO2e
Source: Regulation (EU) 2023/1773, Annex II

Step 8 [PRECURSOR]
Description: Total Precursor Emissions (3 materials)
Formula: Sum of all precursors = 172.0500
Result: 172.0500 tCO2e

Step 9 [FINANCIAL]
Description: Total carbon tax liability (full ETS price)
Formula: 303.4187 tCO2e × €85.00/ton = €25,790.59
Result: €25,790.59 EUR
Source: Regulation (EU) 2023/956, Article 21

Step 10 [FINANCIAL]
Description: CBAM phase-in adjustment (2.5% of full price)
Formula: €25,790.59 × 0.025 = €644.76
Result: €644.76 EUR
Source: Regulation (EU) 2023/956, Article 36
```

### 📊 Çıktı Formatı

**JSON Çıktı Örneği**:

```json
{
  "input_summary": {
    "facility": "ABC Döküm Sanayi",
    "facility_id": "TR-IST-001",
    "period": "2026-03",
    "production": 500.0,
    "electricity": 200.0,
    "natural_gas": 15000.0,
    "coal": 0.0,
    "process_inputs": true,
    "precursors_count": 3
  },
  "emissions": {
    "scope_1_direct": 31.81,
    "scope_2_indirect": 86.00,
    "process_emissions": 13.56,
    "precursor_emissions": 172.05,
    "total_emissions": 303.42,
    "natural_gas_emissions": 31.81,
    "coal_emissions": 0.00,
    "electricity_emissions": 86.00,
    "emission_intensity_per_ton": 0.607,
    "energy_intensity_mwh_per_ton": 0.400
  },
  "financials": {
    "total_emissions_tco2e": 303.42,
    "free_allocation_tco2e": 0.0,
    "net_liable_emissions_tco2e": 303.42,
    "ets_price_eur_per_ton": 85.00,
    "total_liability_eur": 25790.59,
    "liability_per_ton_steel_eur": 51.58,
    "cbam_phase_factor": 0.025,
    "effective_liability_eur": 644.76
  },
  "confidence_score": 0.97,
  "anomalies": [],
  "is_compliant": true,
  "compliance_notes": [
    "✅ All checks passed. Data is suitable for CBAM reporting."
  ],
  "audit_timestamp": "2026-03-06T14:30:00",
  "auditor_version": "2.0.0",
  "regulatory_framework": "Regulation (EU) 2023/956, Regulation (EU) 2023/1773"
}
```

### 📊 Auditor Kullanım Örnekleri

#### Temel Auditor Kullanımı

```python
from src.agents.auditor import AuditorEngine, InputPayload

# Input verisi
input_data = InputPayload(
    facility_name="ABC Döküm Sanayi",
    facility_id="TR-IST-001",
    reporting_period="2026-03",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0,
    coal_consumption_tons=0.0,
    data_source="manual"
)

# Auditor oluştur
auditor = AuditorEngine(
    strict_physics=False,
    cbam_phase_factor=0.025,  # 2026: 2.5%
    free_allocation=0.0
)

# Audit yap
result = auditor.audit(input_data)

# Sonuçları göster
print(f"Toplam Emisyon: {result.emissions.total_emissions:.2f} tCO2e")
print(f"Mali Yük: €{result.financials.effective_liability_eur:,.2f}")
print(f"Güven Skoru: {result.confidence_score*100:.0f}%")
```

#### Gelişmiş Kullanım (v2.0 - Tüm Özellikler)

```python
from src.agents.auditor import (
    AuditorEngine, 
    InputPayload, 
    ProcessInputs, 
    PrecursorInput
)

# v2.0 - Tam veri seti
input_data = InputPayload(
    facility_name="ABC Steel Works",
    facility_id="TR-IST-001",
    reporting_period="2026-03",
    production_quantity_tons=500.0,
    
    # Enerji tüketimi
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0,
    coal_consumption_tons=0.0,
    data_source="scada",
    
    # v2.0 - Process inputs
    process_inputs=ProcessInputs(
        electrode_consumption_ton=2.5,
        limestone_consumption_ton=10.0
    ),
    
    # v2.0 - Precursors
    precursors=[
        PrecursorInput(
            material_name="ferro-manganese",
            quantity_ton=5.0,
            embedded_emissions_factor=1.65  # Gerçek tedarikçi verisi
        ),
        PrecursorInput(
            material_name="ferro-silicon",
            quantity_ton=3.0,
            embedded_emissions_factor=None  # CBAM default
        ),
        PrecursorInput(
            material_name="scrap-steel",
            quantity_ton=450.0,
            embedded_emissions_factor=0.35
        )
    ]
)

# Auditor
auditor = AuditorEngine(
    strict_physics=True,  # Strict mode
    cbam_phase_factor=0.025,
    free_allocation=0.0
)

# Audit
result = auditor.audit(input_data, ets_price_override=90.0)

# Detaylı sonuçlar
print("="*70)
print("CBAM AUDIT REPORT")
print("="*70)
print(f"Facility: {result.input_summary['facility']}")
print(f"Period: {result.input_summary['period']}")
print()
print("EMISSIONS BREAKDOWN:")
print(f"  Scope 1 (Fuel):        {result.emissions.scope_1_direct:>10.2f} tCO2e")
print(f"  Scope 2 (Electricity): {result.emissions.scope_2_indirect:>10.2f} tCO2e")
print(f"  Process Emissions:     {result.emissions.process_emissions:>10.2f} tCO2e")
print(f"  Precursor Emissions:   {result.emissions.precursor_emissions:>10.2f} tCO2e")
print(f"  {'-'*50}")
print(f"  TOTAL:                 {result.emissions.total_emissions:>10.2f} tCO2e")
print()
print(f"CONFIDENCE SCORE: {result.confidence_score*100:.0f}%")
print()
print("FINANCIAL IMPACT:")
print(f"  ETS Price:         €{result.financials.ets_price_eur_per_ton:,.2f}/ton")
print(f"  Total Liability:   €{result.financials.total_liability_eur:,.2f}")
print(f"  Effective (2.5%):  €{result.financials.effective_liability_eur:,.2f}")
print(f"  Per Ton Steel:     €{result.financials.liability_per_ton_steel_eur:,.2f}/ton")
print()
print(f"COMPLIANCE: {'✅ COMPLIANT' if result.is_compliant else '❌ NON-COMPLIANT'}")

# Audit trail'i kaydet
with open("audit_trail.txt", "w") as f:
    f.write(auditor.get_audit_trail_text())
```

---

## 🔄 Ajanlar Arası İş Akışı

### Tipik Kullanım Senaryosu

```text
┌─────────────────────────────────────────────────────────────┐
│ Adım 1: Mevzuat Belgelerini Okuma (AJAN #1)                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ PDF Dosyaları
                           ▼
                ┌──────────────────────┐
                │  Data Extractor      │
                │  (Ajan #1)           │
                │                      │
                │  - PDF okuma         │
                │  - LLM extraction    │
                │  - JSON export       │
                └──────────┬───────────┘
                           │
                           │ Yapılandırılmış JSON
                           │ (Mevzuat bilgileri)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Adım 2: Operasyonel Veri Toplama (Manuel/SCADA)             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Tesis Verileri
                           │ (Üretim, enerji, yakıt)
                           ▼
                ┌──────────────────────┐
                │  Auditor Engine      │
                │  (Ajan #2)           │
                │                      │
                │  - Validasyon        │
                │  - Hesaplama         │
                │  - Mali tahmin       │
                └──────────┬───────────┘
                           │
                           │ Audit Raporu
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Adım 3: CBAM Uyumluluk Raporlama                            │
└─────────────────────────────────────────────────────────────┘
```

### Entegre Örnek

```python
# ============================================
# FULL WORKFLOW: PDF → Audit Report
# ============================================

from src.agents.data_extractor import DataExtractor
from src.agents.auditor import AuditorEngine, InputPayload, ProcessInputs

# ============================================
# STEP 1: Mevzuat Anlaşılması (Ajan #1)
# ============================================
extractor = DataExtractor(llm_provider="gemini")

regulation = extractor.process_document(
    pdf_path="mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf"
)

print("Mevzuat Bilgileri:")
print(f"  Belge: {regulation['document_name']}")
print(f"  Sektörler: {regulation['sectors_covered']}")
print(f"  Son Tarih: {regulation['compliance_deadlines']}")

# ============================================
# STEP 2: Emisyon Hesaplama (Ajan #2)
# ============================================
auditor = AuditorEngine(cbam_phase_factor=0.025)

input_data = InputPayload(
    facility_name="ABC Döküm Sanayi",
    reporting_period="2026-Q1",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0,
    
    process_inputs=ProcessInputs(
        electrode_consumption_ton=2.5,
        limestone_consumption_ton=10.0
    )
)

audit_result = auditor.audit(input_data)

# ============================================
# STEP 3: Raporlama
# ============================================
report = {
    "regulation_framework": regulation['document_name'],
    "facility": audit_result.input_summary['facility'],
    "reporting_period": audit_result.input_summary['period'],
    "total_emissions_tco2e": audit_result.emissions.total_emissions,
    "financial_liability_eur": audit_result.financials.effective_liability_eur,
    "compliance_status": "COMPLIANT" if audit_result.is_compliant else "NON-COMPLIANT",
    "confidence_score": audit_result.confidence_score,
    "submission_deadline": regulation['compliance_deadlines'][0]['date']
}

print("\n" + "="*70)
print("CBAM COMPLIANCE REPORT")
print("="*70)
for key, value in report.items():
    print(f"{key:.<40} {value}")
```

---

## 📚 Kaynaklar ve Referanslar

### Yasal Çerçeve

- **Regulation (EU) 2023/956**: CBAM Framework
- **Regulation (EU) 2023/1773**: CBAM Implementation (Annexes)
- **Directive 2003/87/EC**: EU ETS
- **IPCC (2006)**: Greenhouse Gas Inventories Guidelines
- **Commission Decision 2011/278/EU**: Benchmarks for Free Allocation

### Teknik Dokümantasyon

- **CBAM Guidance Document**: Implementation for Installation Operators
- **IEA Energy Technology Perspectives 2020**: Steel Industry Benchmarks
- **TEİAŞ 2024 Report**: Turkish Electricity Grid Emission Factors

---

## 📞 Destek ve Katkı

### Test Dosyaları

- `test_auditor.py`: Ajan #2 test suite
- `test_v2_upgrade.py`: v2.0 özellikler testi
- `examples/run_data_extractor.py`: Ajan #1 örnek kullanım
- `examples/demo_v3_features.py`: v3.0 özellikleri demo

### Dokümantasyon

- `README.md`: Genel sistem dokümantasyonu
- `CHANGELOG.md`: Versiyon geçmişi
- `UPGRADE_V2_SUMMARY.md`: v2.0 yükseltme özeti
- `KURULUM.md`: Kurulum talimatları (Türkçe)

---

**Son Güncelleme**: 6 Mart 2026  
**Sistem Versiyonları**: Data Extractor v3.0, Auditor Engine v2.0
