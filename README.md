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

---
## Son Eklenenler (Ozet)

- Data Quality Guard katmani eklendi.
- Pipeline tarafinda fail-fast validasyon (Stage 2.5) aktif edildi.
- API tarafinda data quality hatalari icin kural kodlu 422 cevap modeli eklendi.
- Frontend upload akisinda data quality hatalari kullaniciya aksiyon odakli gosterilmeye baslandi.
- Frontend sayfalarinda TR/EN i18n kapsami genisletildi.

## Hizli Inceleme Sirasi

1. PROJE_KONTROL.md dosyasindaki guncel durum notlarini oku.
2. src/api.py icinde /api/upload ve /api/validate-payload akislarini incele.
3. src/pipeline.py icindeki Stage 2 -> Stage 2.5 -> Stage 3 akisina bak.
4. src/agents/guards/schema_guard.py icindeki business-rule kontrollerini kontrol et.

---

## Bugun Yapilan Degisiklikler (Detayli)

Bu bolum, bugun UI/UX ve entegrasyon tarafinda yapilan tum iyilestirmeleri teknik akisla birlikte detaylandirir.

### 1) Enterprise ve Orchestrator Altyapisi

- Orchestrator job lifecycle katmani, asenkron denetim calistirma modelini standartlastiracak sekilde canliya alindi.
- FastAPI tarafinda job submit ve status endpointleri ile API tabanli is takibi netlestirildi.
- ExplainabilityAgent ile denetim sonucu yalnizca sayisal rapor olmaktan cikarilip regulator odakli izlenebilir adimlar (audit trail) ile guclendirildi.
- RegressionAgent entegrasyonu ile emisyon/vergi hesaplarinda baseline uyumu korunarak CI/CD ortaminda dogrulanabilirlik arttirildi.
- Bu katmanin birim ve entegrasyon testleriyle guard red, basarili tamamlama ve hata izolasyonu gibi kritik senaryolar kapsandi.

### 2) Upload -> Orchestrator Baglantisi (Uctan Uca Akis)

- Frontend upload akisi, native fetch cagrilarindan cikarilarak merkezi API istemcisi ve JobService etrafinda toplandi.
- Upload sonrasi job submit + polling + tamamlanan sonucun gosterimi tek bir tutarli akis haline getirildi.
- JobId state yonetimi netlestirildi ve backend status degisimleri (PENDING/RUNNING/COMPLETED/FAILED/REJECTED_BY_GUARD) UI tarafina reaktif sekilde baglandi.
- Yeniden kullanilabilir useJobPolling hook'u ile polling baslatma, sonlandirma ve hata durumlarinda kontrollu kapanis mekanizmasi standartlastirildi.

### 3) Data Quality Guard ve Fail-Fast Yaklasimi

- Pipeline oncesi zorunlu validasyon adimi eklenerek hatali payload'larin denetim zincirine girmeden erken reddedilmesi saglandi.
- API tarafinda data quality ihlalleri icin kodlu ve yapisal 422 cevap modeli kullanima alindi.
- Frontend upload ekraninda bu 422 cevaplari kullaniciya sadece hata metni olarak degil:
  - kural kodu,
  - aciklama,
  - aksiyon odakli yonlendirme
  formatinda gosterilecek sekilde iyilestirildi.

### 4) ExecutiveConsultingReport UI Donusumu

- Upload tamamlanma ekranindaki ham JSON dump (pre/code blok) kaldirildi.
- Yerine yonetici odakli ozet panel akisi tasarlandi:
  1. AI Consultant Summary,
  2. KPI Cards,
  3. 5-Year Tsunami Chart.
- Bu donusum ile "ham veri gosteren teknik ekran" modelinden "karar destek dashboard" modeline gecildi.

### 5) KPI Cards Bileseni

- Yeni KPI Cards bileseni ile ExecutiveConsultingReport icindeki kritik metrikler tek bakista sunuldu:
  - Readiness Score,
  - 2026 Estimated Tax,
  - Total CBAM Emissions.
- Readiness degerine gore risk rengi dinamiklestirildi:
  - 70 alti: yuksek risk tonu,
  - 80 ustu: dusuk risk tonu,
  - ara bant: dikkat tonu.
- Veri eksikligi durumlari sifirla maskelemek yerine N/A ile gosterilerek yoneticinin yanlis yorum yapmasi engellendi.

### 6) Tsunami Chart (5 Yillik Vergi Projeksiyonu)

- Recharts tabanli yeni bar chart ile bes yillik vergi artisi trendi gorunsellestirildi.
- Projection object -> chart data array donusumu komponent icinde standart hale getirildi.
- Y ekseni ve tooltip EUR formatina baglandi; artan mali riskin algilanmasi icin bar rengi risk odakli secildi.
- Veri yoksa bos chart yerine anlasilir bir empty-state mesaji gosterilerek UX saglamlastirildi.

### 7) Sonuc Ekrani Zenginlestirmeleri

- Analysis Complete bandi altina readiness tabanli risk badge eklendi.
- AI summary kutusuna metadata etiketleri eklendi:
  - Readiness yuzdesi,
  - Early Warning Signal,
  - Job ID.
- Early Warning katmani readiness skoruyla sinirli kalmayacak sekilde backend compliance/risk sinyalleri ile birlestirildi.
- Korumaci siniflandirma stratejisi uygulandi: birden fazla risk sinyali varsa daha yuksek risk seviyesi tercih edildi.

### 8) i18n Genislemesi ve Sinyal Etiketleme

- Upload sonuc ekranindaki yeni metinler (risk, summary, signal vb.) TR/EN ceviri anahtarlarina tasindi.
- Backend'den gelen teknik sinyal kodlari (ornegin non_compliant, rejected_by_guard) kullanici dostu etiketlere cevrildi.
- Dashboard widget basliklari, N/A metinleri ve chart empty-state metinleri de i18n kapsamina alindi.

### 9) Locale-Aware Sayisal/Para Formatlama

- KPI ve chart bilesenlerinde sayi/para gostergeleri aktif dile gore (TR/EN) otomatik formatlanacak sekilde guncellendi.
- Upload sonucundaki readiness gosterimi de ayni locale mantigina baglandi.
- Tekrar eden formatter kodlarini azaltmak icin merkezi formatlama yardimcisi eklendi ve widget'lar bu utility'e tasindi.

### 10) Teknik Etki Ozeti

- Frontend tarafinda ham veri gosteriminden karar destek odakli yonetici paneline gecis tamamlandi.
- Job status takibi, data quality feedback dongusu ve executive rapor gosterimi tek bir tutarli urun akisinda birlestirildi.
- i18n + locale standardizasyonu ile farkli dil senaryolarinda gorunum tutarliligi arttirildi.
- Kod organizasyonu, tekrar eden formatlama mantiginin merkezilesmesiyle daha bakimi kolay bir hale getirildi.

### 11) RecommendationCards Bileseni (Stratejik Eylem Katmani)

- Dashboard icin yeni `RecommendationCards` bileseni eklendi ve AI tarafindan uretilen ust duzey aksiyon onerileri yonetici ekraninda kart bazli bir modelle gosterilir hale getirildi.
- Bilesen, `recommendations` dizisini prop olarak alacak sekilde tasarlandi; veri yoksa bos blok basmamak icin null-donus davranisi ile gereksiz UI kalabaligi engellendi.
- Responsive grid yapisi ile mobilde tek kolon, masaustu gorunumde iki kolon duzeni kullanilarak hem okunabilirlik hem de bilgi yogunlugu dengelendi.
- Her kartta su alanlar standartlastirildi:
  - `strategy_name` (ana baslik),
  - `difficulty` (Low/Medium/High rozet),
  - `action_plan` (yoneticiye yonelik aciklayici metin),
  - finansal metrik alt-gridi (Annual Savings, CAPEX, ROI/Payback).
- Zorluk rozeti renk semantigi ile karar hizi arttirildi:
  - Low: yesil,
  - Medium: sari/turuncu,
  - High: kirmizi.
- Finansal metriklerde para degerleri EUR formatina baglandi; ROI degeri ise yil birimi ile birlikte gosterilerek finansal geri donusun yonetsel yorumlanmasi kolaylastirildi.
- `potential_subsidies` verisi mevcut oldugunda kartin altinda ayri bir tesvik/grant paneli acilarak bu bilginin gozden kacmasi onlendi.
- Bu panelde `lucide-react` ikonlari (odul/tesvik metaforu) kullanilarak metin yogunlugu azaltildi ve taranabilirlik guclendirildi.

### 12) AuditTrail Bileseni (Regulator Uyumlu Izlenebilirlik)

- Dashboard icin yeni `AuditTrail` bileseni eklendi; Explainable AI (XAI) adimlari tek bir resmi panelde bir araya getirilerek AB regulator denetimlerine uygun bir kanit katmani olusturuldu.
- Bilesen, `auditReport` objesi uzerinden calisir:
  - `steps[]` icinde hesaplama adimlari,
  - `legal_disclaimer` icinde yasal cerceve/aciklama metni.
- Ust baslikta resmi/kurumsal bir ton icin hukuk odakli ikon + "Legal & Calculation Audit Trail" basligi kullanildi.
- Her adim ayri bir blokta sunularak denetim okunabilirligi artirildi; her blokta su bilgi hiyerarsisi izlendi:
  - solda `step_name`,
  - sagda belirgin `result_value + unit`,
  - alt satirda `formula_applied` (monospace code stilinde),
  - onun altinda `regulation_reference` (muted + italik, kitap ikonu ile).
- Bu sunum sekli ile "sonuc" tek basina degil, sonuca giden hesaplama izi ve mevzuat dayanagi ile birlikte gosterilir hale geldi.
- Bilesen altinda yer alan `legal_disclaimer`, raporun hukuki baglamini acikca belirterek yanlis yorum ve baglam kaybi riskini azaltti.

### 13) ExecutiveConsultingReport Ana Akis Entegrasyonu

- Yeni bilesenler upload sonu "analysis completed" gorunumune dogrudan entegre edildi ve mevcut KPI + Tsunami graf ikilisinin altina dogal bir karar akisi eklendi.
- Render sirasi stratejik olarak su sekilde kurgulandi:
  1. KPI Cards,
  2. Tsunami Chart,
  3. Strategic Action Plan (`RecommendationCards`),
  4. ayirici cizgi,
  5. Audit Trail (`AuditTrail`).
- Bu siralama ile once riskin nicel gosterimi (KPI + projeksiyon), sonra aksiyon plani (oneriler), en sonda kanitlanabilir hesaplama/yasal temel (audit trail) veriliyor.
- Son ekran artik yalnizca "rapor gosteren" bir UI degil; yonetici karar sureci + regulatora sunulabilir delil zinciri bir arada sunan butunlesik bir panel kimligi kazandi.
- Teknik olarak entegrasyon, mevcut ExecutiveConsultingReport akisinin davranisini bozmadan (fallback/null-safe render) asamali ve geriye uyumlu sekilde tamamlandi.

### 14) Agent Skills Yonetisim Paketi (Bugun Eklenen Tum Skilller)

Bu bolum, bugun olusturulan/standartlastirilan skill paketini amac, kapsadigi risk ve sistem etkisi acisindan detayli ozetler.

- `agent-contract-registry`:
  Data Miner, Auditor ve Strategist arasindaki JSON/Pydantic kontratlarin tek merkezde versiyonlanmasi, zorunlu alan sozlesmesi ve backward compatibility kontrolu tanimlandi. Bu sayede sessiz schema drift ve entegrasyon kirilmalari erken yakalanabilir hale geldi.
- `payload-mapping-canonicalization`:
  Ham extraction JSON'unun Auditor canonical payload formatina donusumunde unit normalization (kg/lbs, kWh/MWh, m3 vb.), null-safe hata davranisi ve alan bazli provenance baglama kurallari netlestirildi.
- `carbon-math-governance`:
  Emisyon faktorleri, CBAM katsayilari ve vergi formullerinin tek deterministic kaynakta yonetilmesi; finansal hesaplarda Decimal zorunlulugu ve regülasyon referansli formül disiplini standartlastirildi.
- `golden-baseline-regression`:
  Kritik emisyon/vergi hesaplari icin golden dataset karsilastirmasi, tolerans-asiminda fail-fast bloklama ve old/new farklarin analitik diff raporuyla sunulmasi politikasi eklendi.
- `explainability-evidence-composer`:
  Her sayisal ciktiya zorunlu kanit paketi (formul, mevzuat referansi, kaynak/provenance izi, sonuc->ham veri geri izlenebilirligi) baglanarak denetim kalitesi guclendirildi.
- `data-quality-rule-engine`:
  Fiziksel imkansizlik ve business rule kontrollerinin merkezi kural motorunda yonetilmesi, rule_id/rule_version bazli ihlal ciktilari ve orkestrasyondan izole kural yonetimi standardi getirildi.
- `cbam-regulation-delta-tracker`:
  AB CBAM mevzuat degisikliklerinin madde bazli delta takibi, etki haritalama (math/rule/reporting) ve tarihsel hesaplamada doneme uygun hukuki versiyon secimi zorunlulugu eklendi.
- `agent-messaging-error-taxonomy`:
  Coklu ajan mesajlasmasinda envelope standardi (correlation_id, sender/receiver, timestamp) ve domain-ozel hata kodlarina gore deterministic tepki (retry/fallback/dead-letter) sozlesmesi tanimlandi.
- `orchestrator-lifecycle-reliability`:
  Job lifecycle state machine gecisleri, idempotent calisma ilkeleri ve hata kodu sinifina dayali exponential backoff/dead-letter davranisi standartlastirildi.
- `financial-stress-sensitivity-analyzer`:
  ETS fiyati, allocation ve phase-in parametrelerinde baseline/best/worst matris tabanli stres testleri ile parametre etkisinin siralanmasi (sensitivity ranking) modeli eklendi.
- `scenario-simulation-playbook`:
  Strategist senaryolarinin sabit playbook template'leriyle (green shift, efficiency, scrap vb.) kiyaslanabilir CAPEX/OPEX/ROI ciktilari uretmesi ve stres test cagrisi zorunlulugu tanimlandi.
- `api-contract-consistency-guard`:
  Kok API ile moduler endpoint kontratlarinin capraz kontrolu, versiyonsuz breaking change bloklama ve entegrator odakli endpoint-delta raporlamasi tanimlandi.
- `data-provenance-confidence-calibration`:
  Alan bazli provenance kaydi, confidence kalibrasyon mantigi, dusuk-guvenli veriler icin human-in-the-loop kuyruk ve manuel override lineage (eski/yeni/karar sahibi/zaman) standardi eklendi.
- `multi-format-ingestion-assurance`:
  PDF/Excel/CSV/OCR icin format-bazli kalite kapilari, parser fallback hiyerarsisi ve taxonomy uyumlu hata raporlamasi ile ingestion katmani guclendirildi.
- `reporting-payload-design-system`:
  Auditor/Strategist ciktilarinin UI'dan bagimsiz, stabil DTO payload'lara donusmesi; explainability/provenance/confidence metadata'sinin zorunlu tasinmasi prensibi netlestirildi.
- `architecture-guardian-scaffolding`:
  Yeni ajan/modul eklemelerinde zorunlu compliance checklist'i, yuksek-risk degisikliklerde governance gate ve skill-bazli otomatik uyum denetimi icin meta-koruma modeli tanimlandi.

Bu skill paketi birlikte ele alindiginda sistemde su 4 ana kazanci sagladi:

- Sozlesme ve sema disiplini: API/agent arasi kirilmalari erken engelleme.
- Deterministik hesap ve denetlenebilirlik: finansal/carbonsal sonuclarin tekrar uretilebilirligi.
- Orkestrasyon guvenilirligi: hata sinifina gore tutarli lifecycle yonetimi.
- Regulator/yonetim hazir raporlama: aciklanabilir, kanitlanabilir ve entegrasyon dostu cikti.

### 15) Klasor Yapisi Sadelestirme ve Yol Guncellemeleri

- Proje koku sadeleştirildi; yardimci dosyalar amacina gore ayrildi:
  - `bin/`: tum `.bat` calistiricilar,
  - `scripts/js`: yardimci JS scriptleri,
  - `scripts/python`: yardimci Python scriptleri,
  - `src/`: cekirdek API/kurulum scriptleri.
- `api.py` dosyasi `src/api.py` konumuna tasindigi icin:
  - calistirma komutu `python src/api.py` olacak sekilde guncellendi,
  - testlerde modul importu isim cakismasini onleyecek sekilde dosya-yolu bazli yukleme modeline gecildi,
  - API icindeki proje koku/path cozumleme mantigi yeni konuma gore duzeltildi.
- `setup.py` `src/` altina alindiktan sonra `README.md` ve `requirements.txt` okumasi proje kokunden cozulur hale getirildi.

### 16) Dogrulama ve Stabilite Kontrolleri

- Tasima ve yol guncellemeleri sonrasinda API orchestrator testleri tekrar kosuldu.
- `tests/test_api_orchestrator.py` senaryolari basariyla gecti (submit/process/status akislari).
- Lint/syntax seviyesinde degisiklik yapilan kritik dosyalarda hata kalmadigi dogrulandi.
