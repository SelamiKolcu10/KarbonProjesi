# 🚀 Kurulum Rehberi

## Adım Adım Kurulum

### 1️⃣ Python Kontrolü

Python 3.8 veya üzeri gerekli:

```powershell
python --version
```

### 2️⃣ Virtual Environment Oluştur (Önerilen)

```powershell
# Virtual environment oluştur
python -m venv venv

# Aktif et
.\venv\Scripts\Activate.ps1

# Eğer script çalıştırma hatası alırsanız:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3️⃣ Bağımlılıkları Yükle

```powershell
# Tüm paketleri yükle
pip install -r requirements.txt

# VEYA tek tek:
pip install pdfplumber pypdf
pip install google-generativeai openai
pip install python-dotenv requests
pip install pandas numpy
pip install rich tqdm
pip install pytest black flake8
```

### 4️⃣ API Anahtarlarını Ayarla

```powershell
# .env dosyasını oluştur
copy .env.example .env

# .env dosyasını notepad ile aç
notepad .env
```

`.env` içine API anahtarınızı ekleyin:

```env
# Gemini kullanacaksanız:
GEMINI_API_KEY=AIzaSy...your_actual_key_here
DEFAULT_LLM_PROVIDER=gemini

# VEYA GPT kullanacaksanız:
OPENAI_API_KEY=sk-proj-...your_actual_key_here
DEFAULT_LLM_PROVIDER=gpt
```

### 5️⃣ API Anahtarı Nasıl Alınır?

#### Gemini API Key (ÜCRETSİZ - Önerilen)

1. [Google AI Studio](https://aistudio.google.com/)'ya gidin
2. Google hesabınızla giriş yapın
3. "Get API Key" butonuna tıklayın
4. Yeni API key oluşturun
5. Anahtarı kopyalayıp `.env` dosyasına yapıştırın

#### OpenAI API Key (Ücretli)

1. [OpenAI Platform](https://platform.openai.com/)'a gidin
2. Hesap oluşturun ve kredi kartı ekleyin
3. API Keys bölümünden yeni key oluşturun
4. Anahtarı kopyalayıp `.env` dosyasına yapıştırın

### 6️⃣ Test Et

```powershell
# Basit test
python examples\simple_usage.py

# Detaylı test
python examples\run_data_extractor.py

# Unit testler
pytest tests\
```

## ⚠️ Sorun Giderme

### Hata: "pdfplumber could not be resolved"

**Çözüm:** Paketler henüz yüklenmemiş

```powershell
pip install pdfplumber
```

### Hata: "GEMINI_API_KEY bulunamadı"

**Çözüm:** `.env` dosyasını oluşturun

```powershell
copy .env.example .env
notepad .env
# API anahtarınızı ekleyin
```

### Hata: "Script execution is disabled"

**Çözüm:** PowerShell execution policy'yi ayarlayın

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Hata: "Module not found"

**Çözüm:** Virtual environment aktif değil veya paketler yüklenmemiş

```powershell
# Virtual environment'ı aktif edin
.\venv\Scripts\Activate.ps1

# Paketleri tekrar yükleyin
pip install -r requirements.txt
```

## ✅ Kurulum Tamamlandı

Artık Data Extractor'ı kullanabilirsiniz:

```python
from src.agents.data_extractor import DataExtractor

extractor = DataExtractor(llm_provider="gemini")
result = extractor.process_document(
    pdf_path="mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf",
    output_path="output/data.json"
)
```

## 📚 Sonraki Adımlar

1. README.md dosyasını okuyun
2. examples/ klasöründeki örneklere bakın
3. Kendi PDF'lerinizi işlemeye başlayın!
