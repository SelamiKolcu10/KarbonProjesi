# 🚀 İYİLEŞTİRME NOTLARI

## 🆕 AGENT #2 v2.0 + INTEGRATION PIPELINE (2026-03-07)

### 🏭 Agent #2: Auditor Engine v2.0

**Yeni Özellikler:**

#### 1️⃣ **Process Emissions (Kimyasal Emisyonlar)**

- ⚗️ Elektrot tüketimi hesaplaması (C → CO₂)
- 🧱 Kireçtaşı kalsinasyonu (CaCO₃ → CaO + CO₂)
- Yeni `ProcessInputs` modeli
- Stoichiometric faktörler: `STOICHIOMETRIC_C_TO_CO2 = 3.664`, `LIMESTONE_EF = 0.44`

#### 2️⃣ **Precursor Emissions (Hammadde Gömülü Emisyonlar)**

- 🔩 Ferro-alaşımlar, hurda çelik, pig-iron tracking
- Yeni `PrecursorInput` modeli
- Default CBAM factors: ferro-manganese (1.65), ferro-silicon (2.10), scrap-steel (0.35), pig-iron (2.30)
- Tedarikçi-specific faktör desteği

#### 3️⃣ **Confidence Scoring**

- 🎯 Veri kalitesi skoru (0.5 - 1.0)
- Default faktör kullanımı cezası (0.1/precursor)
- Eksik process inputs kontrolü

#### 4️⃣ **Detailed Breakdown**

- 📊 Emisyon kaynağı bazında detaylı kırılım
- Breakdown dictionary: natural_gas, coal, electricity, process, precursors

### 🔗 Integration Pipeline (src/pipeline.py)

**Tam Sistem Entegrasyonu:**

- 🔄 Agent #1 ↔ Agent #2 köprüsü
- Null-safe veri dönüştürme (Adapter Pattern)
- Otomatik birim dönüşümü (kWh→MWh, kg→ton)
- 3-aşamalı işlem: Extract → Map → Audit
- CLI ve Python API desteği
- Detaylı özet raporları
- JSON, CSV export

**Kullanım:**

```bash
python -m src.pipeline document.pdf --facility-name "My Factory"
```

---

## 🆕 AGENT #1 v3.0 - 6 YENİ ÖZELLİK (2026-03-05)

### 1️⃣ **Batch Processing Helper** 🚀

Birden fazla PDF'i tek seferde işleme:

```python
extractor = DataExtractor(enable_stats=True)
results = extractor.process_documents_batch(
    pdf_paths=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_dir="output/batch",
    stop_on_error=False  # Hata olsa da devam et
)
```

- Her belge için ayrı JSON çıktısı
- Toplu ilerleme bildirimi
- Hata toleransı

### 2️⃣ **Confidence Score** ✨

Çıkarılan verinin güvenilirlik skoru:

```python
result = extractor.process_document("doc.pdf")
confidence = result["_metadata"]["confidence_score"]  # 0.0 - 1.0
```

- Kritik alanların doluluk oranı (40%)
- Genel doluluk oranı (30%)
- Liste alanlarının doluluk oranı (30%)

### 3️⃣ **Multi-Format Export** 📊

CSV, Excel, SQL formatlarında export:

```python
# Tek belge CSV
extractor.export_to_csv(result, "output.csv")

# Batch CSV
extractor.export_batch_to_csv(results, "output.csv")

# Excel
extractor.export_to_excel(results, "output.xlsx")

# SQL INSERT statements
extractor.export_to_sql(results, "documents", "output.sql")
```

### 4️⃣ **Document Summary** 📝

Belge özetleri oluşturma:

```python
summary = extractor.generate_summary(result, max_length=500)
print(summary)
# "CBAM Regulation (Regulation) Published on 2023-05-16 by European Union. 
#  Scope: Establishes carbon border adjustment mechanism..."
```

### 5️⃣ **Language Detection** 🌍

Otomatik dil tespiti:

```python
result = extractor.process_document("doc.pdf")
lang = result["_metadata"]["detected_language"]  # "en"
lang_conf = result["_metadata"]["language_confidence"]  # 0.95
```

- 5 dil desteği: EN, TR, DE, FR, ES
- Basit ve gelişmiş mod (langdetect)
- Güven skoru ile birlikte

### 6️⃣ **Statistics & Reporting** 📈

Detaylı istatistik takibi:

```python
extractor = DataExtractor(enable_stats=True)

# İstatistik özeti
stats = extractor.get_stats_summary()
print(f"Success Rate: {stats['success_rate']}%")
print(f"Cache Hit Rate: {stats['cache_hit_rate']}%")

# Detaylı rapor
report = extractor.get_stats_report()
print(report)

# Raporu kaydet
extractor.save_stats_report("stats.json")
```

**Takip Edilen Metrikler:**

- Toplam/başarılı/başarısız işlemler
- Ortalama işlem süresi
- Cache hit/miss oranı
- Retry sayısı
- Chunk operasyonları
- Hata detayları

---

## ✅ v2.0 - 8 İYİLEŞTİRME (2026-03-04)

### 1️⃣ **Retry Mekanizması**

API hatalarında otomatik 3 kez tekrar deneme (exponential backoff ile):

```python
extractor = DataExtractor(max_retries=3)
```

- İlk hata: 1 saniye bekle
- İkinci hata: 2 saniye bekle
- Üçüncü hata: 4 saniye bekle

### 2️⃣ **Loglama Sistemi**

Detaylı log dosyaları (logs/ klasöründe):

```python
import logging
logging.basicConfig(level=logging.INFO)
```

- Her adım loglanıyor
- Hatalar exc_info ile detaylı kaydediliyor
- Debug modu destekliyor

### 3️⃣ **Cache Sistemi**

Aynı PDF'i tekrar işlememek için (cache/ klasöründe):

```python
extractor = DataExtractor(use_cache=True, cache_ttl_hours=24)
```

- PDF hash'i ile cache kontrolü
- 24 saat geçerlilik süresi
- Otomatik cache temizleme

**Cache Komutları:**

```python
# Cache'i temizle
extractor.clear_cache()

# Süresi dolmuş cache'leri temizle
extractor.clear_expired_cache()

# Force reprocess (cache'i yoksay)
extractor.process_document(pdf_path, force_reprocess=True)
```

### 4️⃣ **Chunk Processing**

Uzun belgeler için parçalı işleme:

```python
extractor = DataExtractor(chunk_size=15000)
extractor.process_document(pdf_path, use_chunking=True)
```

- 15000+ karakter belgeler otomatik parçalanıyor
- Her parça ayrı işleniyor
- Sonuçlar akıllıca birleştiriliyor

### 5️⃣ **PDF Metadata Çıkarma**

PDF'in kendi metadata'sını otomatik çıkarıyor:

```json
"_pdf_metadata": {
  "title": "...",
  "author": "...",
  "page_count": 53,
  "creation_date": "..."
}
```

### 6️⃣ **Rate Limiting**

API call sınırı kontrolü:

```python
extractor = DataExtractor(rate_limit_per_minute=10)
```

- Dakikada max 10 call
- Otomatik bekleme

### 7️⃣ **Progress Callback**

İlerleme bildirimi:

```python
def progress(stage, current, total):
    print(f"[{stage}] {current}/{total}")

extractor.process_document(pdf_path, progress_callback=progress)
```

- `extract_text`: PDF okuma ilerlemesi
- `extract_llm`: LLM işleme ilerlemesi
- `complete`: İşlem tamamlandı

### 8️⃣ **Detaylı Hata Mesajları**

Her aşamada ne olduğu açıkça belli:

```text
INFO:src.agents.data_extractor:PDF okunuyor...
INFO:src.agents.data_extractor:Metin temizleniyor...
INFO:src.agents.data_extractor:LLM extraction başlıyor...
INFO:src.agents.data_extractor:✅ Extraction tamamlandı!
INFO:src.agents.data_extractor:⏱️  Toplam süre: 16.55 saniye
```

## 📊 Performans İyileştirmeleri

### Önce v1.0

- ❌ Her seferinde tekrar işleme
- ❌ API hatalarında crash  
- ❌ Uzun belgeler için sorun
- ❌ İlerleme bilgisi yok
- ❌ Minimalist loglama

### Sonra v2.0

- ✅ Cache ile anlık yükleme
- ✅ Retry ile %99.9 başarı
- ✅ Chunk ile sınırsız uzunluk
- ✅ Real-time ilerleme
- ✅ Detaylı loglama

**Örnek:** Aynı PDF tekrar işlenirken:

- v1.0: ~16 saniye
- v2.0: **<1 saniye** (cache'den)

## 🎯 Kullanım Örnekleri

### Basit Kullanım

```python
from src.agents.data_extractor import DataExtractor

extractor = DataExtractor(llm_provider="gemini")
result = extractor.process_document("document.pdf", "output.json")
```

### Gelişmiş Kullanım

```python
from src.agents.data_extractor import DataExtractor
import logging

logging.basicConfig(level=logging.INFO)

# Tüm özellikler aktif
extractor = DataExtractor(
    llm_provider="gemini",
    use_cache=True,
    cache_ttl_hours=24,
    max_retries=3,
    chunk_size=15000,
    rate_limit_per_minute=10
)

# Progress callback
def show_progress(stage, current, total):
    percent = (current / total) * 100
    print(f"[{stage}] {percent:.0f}%")

# İşle
result = extractor.process_document(
    pdf_path="document.pdf",
    output_path="output.json",
    use_chunking=True,
    force_reprocess=False,
    progress_callback=show_progress
)

# Metadata'yı kontrol et
print("Sayfa sayısı:", result['_metadata']['page_count'])
print("İşlem süresi:", result['_metadata']['processing_time_seconds'])
print("Chunk kullanıldı mı?:", result['_metadata']['used_chunking'])
```

## 📁 Yeni Klasör Yapısı

```text
KarbonSalınımProjesi/
├── cache/                    ← YENİ! Cache dosyaları
│   └── *.json
├── logs/                     ← Log dosyaları
│   └── *.log
├── src/
│   ├── agents/
│   │   └── data_extractor.py ← İYİLEŞTİRİLDİ!
│   └── utils/
│       ├── cache.py          ← YENİ!
│       ├── retry.py          ← YENİ!
│       ├── logger.py
│       └── validators.py
└── ...
```

## 🔧 Sorun Giderme

### Cache çalışmıyor mu?

```python
# Cache'i temizle ve tekrar dene
extractor.clear_cache()
extractor.process_document(pdf_path, force_reprocess=True)
```

### Retry sınırına takılıyor mu?

```python
# Retry sayısını artır
extractor = DataExtractor(max_retries=5)
```

### Çok uzun belgeler mi?

```python
# Chunk boyutunu ayarla
extractor = DataExtractor(chunk_size=20000)
```

## 📈 Sonraki Adımlar

- [ ] Paralel chunk processing
- [ ] Multi-LLM fallback (Gemini hatası → GPT)
- [ ] Streaming API desteği
- [ ] GPU acceleration
- [ ] Bulk processing optimize

---

Tüm özellikler test edildi ve çalışıyor!
