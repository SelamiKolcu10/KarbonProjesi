# 🤖 Karbon Salınımı Agentic AI Projesi

CBAM (Carbon Border Adjustment Mechanism) belgelerinden otomatik veri çıkarımı ve uyumluluk denetimi yapan agentic AI sistemi.

## 🎯 Sistem Mimarisi

```text
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Agent #1  │ ───> │  Pipeline   │ ───> │   Agent #2   │
│  Extractor  │ JSON │   Adapter   │ Data │   Auditor    │
│   (v3.0)    │      │             │      │   (v2.0)     │
└─────────────┘      └─────────────┘      └──────────────┘
     PDF/Excel           Mapping           Compliance Report
```

## 📋 Özellikler

### Ajan #1: Data Extractor ⭐ v3.0 (FULL-FEATURED)

✅ PDF belgelerini okur (pdfplumber) - **53 sayfa/saniyede**  
✅ Metni temizler ve normalleştirir  
✅ LLM ile yapılandırılmış veri çıkarır (Gemini veya GPT)  
✅ Sadece belgede mevcut olan bilgileri çıkarır  
✅ Eksik veriler için 'NULL' döner (asla uydurma yapmaz)  
✅ Standart JSON şeması kullanır  

#### 🆕 Yeni Özellikler (v3.0) - 6 Büyük Ekleme

🚀 **Batch Processing** - Birden fazla PDF'i tek seferde işleme  
✨ **Confidence Score** - Çıkarılan verinin güvenilirlik skoru (0.0-1.0)  
📊 **Multi-Format Export** - CSV, Excel, SQL formatlarında export  
📝 **Document Summary** - Otomatik belge özeti oluşturma  
🌍 **Language Detection** - 5 dilde otomatik dil tespiti  
📈 **Statistics & Reporting** - Detaylı işlem istatistikleri  

#### ✨ v2.0 Özellikleri

✨ **Retry Mekanizması** - API hatalarında 3 kez otomatik tekrar deneme  
✨ **Loglama Sistemi** - Detaylı log dosyaları (logs/)  
✨ **Cache Sistemi** - Aynı PDF'i tekrar işlememek için (<1 saniye!)  
✨ **Chunk Processing** - Uzun belgeler için parçalı işleme  
✨ **PDF Metadata** - Otomatik metadata çıkarma  
✨ **Rate Limiting** - API call sınırı kontrolü  
✨ **Progress Callback** - Real-time ilerleme bildirimi  
✨ **Detaylı Hata Mesajları** - Her adım loglanıyor  

[CHANGELOG.md](CHANGELOG.md)'de tüm yeni özellikler detaylı açıklanıyor.

### Ajan #2: Auditor Engine ⭐ v2.0 (CHEMISTRY-ENABLED)

✅ Scope 1 & 2 emisyon hesaplamaları
✅ **Process Emissions** - Elektrot ve kireçtaşı kalsinasyonu  
✅ **Precursor Emissions** - Hammadde gömülü emisyonları  
✅ **Confidence Scoring** - Veri kalitesi değerlendirmesi  
✅ Fizik-tabanlı validasyon (enerji yoğunluğu kontrolleri)  
✅ Mali etki analizi (EU ETS carbon pricing)  
✅ CBAM phase-in desteği (2026-2034)  
✅ Detaylı audit trail  
✅ Anomali tespiti  

#### 🆕 v2.0 Özellikleri

⚗️ **Process Emissions** - Kimyasal reaksiyon emisyonları  
🔩 **Precursor Tracking** - Ferro-alaşımlar, hurda çelik, pig-iron  
🎯 **Confidence Score** - AI-powered veri kalitesi skoru  
📊 **Breakdown Dictionary** - Kaynak bazında detaylı kırılım  

### 🔗 Integration Pipeline (FULL-STACK)

✅ Agent #1 ↔ Agent #2 entegrasyonu  
✅ Null-safe veri dönüştürme  
✅ Otomatik birim dönüşümü  
✅ CLI + Python API  
✅ Detaylı raporlama  

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.8+
- Gemini API Key VEYA OpenAI API Key

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Ayarla

`.env.example` dosyasını `.env` olarak kopyalayın ve API anahtarlarınızı girin:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
# VEYA
OPENAI_API_KEY=your_actual_openai_api_key_here

DEFAULT_LLM_PROVIDER=gemini
```

## 💡 Kullanım

### Basit Kullanım

```python
from src.agents.data_extractor import DataExtractor

# Data Extractor oluştur
extractor = DataExtractor(llm_provider="gemini")

# PDF'i işle
result = extractor.process_document(
    pdf_path="mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf",
    output_path="output/extracted_data.json"
)

# Sonuçları kullan
print(result['document_name'])
print(result['publication_date'])
```

### Detaylı Örnek

```bash
python examples/run_data_extractor.py
```

### Agent #2 Kullanımı (Auditor)

```python
from src.agents.auditor import AuditorEngine
from src.agents.auditor.models import InputPayload

# Audit engine oluştur
auditor = AuditorEngine(
    strict_physics=False,
    cbam_phase_factor=0.025,  # 2026: 2.5% phase-in
    free_allocation=0.0
)

# Input data hazırla
payload = InputPayload(
    facility_name="ABC Döküm Sanayi",
    reporting_period="2026-03",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0
)

# Audit yap
result = auditor.audit(payload)

# Sonuçlar
print(f"Total Emissions: {result.emissions.total_emissions:.2f} tCO2e")
print(f"Financial Liability: €{result.financials.effective_liability_eur:,.2f}")
print(f"Compliance: {result.is_compliant}")
```

### Full Pipeline Kullanımı

```python
from src.pipeline import run_analysis

# Tek komutla complete analysis
results = run_analysis(
    file_path="factory_invoice.pdf",
    facility_name="My Steel Factory",
    llm_provider="gemini",
    use_cache=True
)

# Özet
print(f"Total Emissions: {results['summary']['total_emissions_tco2e']:.2f} tCO2e")
print(f"Liability: €{results['summary']['financial_liability_eur']:,.2f}")
print(f"Status: {results['summary']['compliance_status']}")
```

**CLI:**

```bash
python -m src.pipeline document.pdf --facility-name "ABC Steel"
```

## 📊 Çıktı Şeması

Data Extractor aşağıdaki JSON şemasını döndürür:

```json
{
  "document_name": "string or NULL",
  "document_number": "string or NULL",
  "document_type": "string or NULL",
  "publication_date": "YYYY-MM-DD or NULL",
  "effective_date": "YYYY-MM-DD or NULL",
  "issuing_authority": "string or NULL",
  "legal_basis": "string or NULL",
  "scope": "string or NULL",
  "sectors_covered": ["array or NULL"],
  "emissions_categories": ["array or NULL"],
  "key_obligations": ["array or NULL"],
  "reporting_requirements": "string or NULL",
  "compliance_deadlines": [
    {
      "date": "YYYY-MM-DD",
      "description": "string"
    }
  ],
  "penalties": "string or NULL",
  "relevant_articles": ["array or NULL"],
  "_metadata": {
    "source_file": "filename.pdf",
    "extraction_date": "2026-03-04 12:30:00",
    "llm_provider": "gemini",
    "text_length": 45678
  }
}
```

## 🔑 Önemli Özellikler

### NULL Değer Yönetimi

Eğer belgede bir bilgi **açıkça belirtilmemişse**, o alan için `"NULL"` değeri döner. Sistem asla bilgi uydurmaz:

```json
{
  "document_name": "Regulation (EU) 2023/956",
  "publication_date": "2023-05-16",
  "some_missing_field": "NULL"  // ← Belgede yok
}
```

### LLM Provider Değiştirme

```python
# Gemini kullan
extractor = DataExtractor(llm_provider="gemini")

# GPT kullan
extractor = DataExtractor(llm_provider="gpt")
```

## 📁 Proje Yapısı

```text
KarbonSalınımProjesi/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── data_extractor.py    # Ana ajan modülü
│   ├── utils/
│   │   ├── logger.py             # Loglama
│   │   └── validators.py         # Validasyon
│   └── config.py                 # Konfigürasyon
├── examples/
│   ├── run_data_extractor.py     # Detaylı örnek
│   └── simple_usage.py           # Basit örnek
├── mevzuat_docs/                 # PDF belgeleri
├── output/                       # Çıktı JSON dosyaları
├── logs/                         # Log dosyaları
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Konfigürasyon

`src/config.py` dosyasında ayarları özelleştirebilirsiniz:

```python
# LLM ayarları
DEFAULT_LLM_PROVIDER = "gemini"  # veya "gpt"
LLM_TEMPERATURE = 0.1            # Düşük = tutarlı
LLM_MAX_TOKENS = 4096

# Text işleme
MAX_TEXT_LENGTH = 15000          # LLM'e gönderilecek max karakter
```

## 📝 Örnek Çıktı

```text
📄 PDF okunuyor: CELEX_32023R0956_EN_TXT.pdf
🧹 Metin temizleniyor... (125847 karakter)
🤖 LLM ile veri çıkarılıyor (GEMINI)...
💾 Veri kaydedildi: output/extracted_data.json
✅ Extraction tamamlandı!

======================================================================
📊 ÇIKARILAN VERİ ÖZETİ
======================================================================

🏛️  Belge Adı: Regulation (EU) 2023/956
📄 Belge No: 32023R0956
📝 Belge Tipi: regulation
📅 Yayın Tarihi: 2023-05-16
⚡ Yürürlük Tarihi: 2023-06-05
🏢 Yayınlayan Kurum: European Parliament and Council

🏭 Kapsanan Sektörler (6):
   • Cement
   • Iron and steel
   • Aluminium
   • Fertilisers
   • Electricity
   ... ve 1 tane daha
```

## 🐛 Hata Ayıklama

Loglar `logs/` klasöründe saklanır:

```bash
logs/data_extractor_example_20260304.log
```

## ✅ Tamamlanan Ajanlar

- [x] **Ajan #1: Data Extractor** (v3.0) - PDF/Excel veri çıkarımı
- [x] **Ajan #2: Auditor Engine** (v2.0) - CBAM compliance audit
- [x] **Integration Pipeline** - Full-stack entegrasyon

## 🔜 Sıradaki Ajanlar

- [ ] **Ajan #3: Compliance Checker** - Detaylı CBAM regulation kontrolü
- [ ] **Ajan #4: Report Generator** - PDF/Excel rapor oluşturma
- [ ] **Ajan #5: Document Classifier** - Belge tipi sınıflandırma

## 📄 Lisans

MIT License

## 👥 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için lütfen önce issue açın.

---

**Not:** Bu proje CBAM mevzuatı analizi için geliştirilmiştir. Gerçek uygulamalarda çıktıları mutlaka doğrulayın.
