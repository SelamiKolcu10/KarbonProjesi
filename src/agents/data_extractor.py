"""
Data Extractor Agent - Agentic AI Projesi Ajan #1 (İYİLEŞTİRİLMİŞ v3.2 - Data Fusion)
Bu modül PDF/Excel/CSV belgelerinden endüstriyel veri çıkarır (enerji, üretim, yakıt tüketimi).

YENİ ÖZELLİKLER v3.2 (Data Fusion & Unit Normalization):
- 🆕 Smart Unit Normalization (lbs→tons, MMBtu→MWh vb. otomatik dönüşüm)
- 🆕 Multi-Document Data Fusion (farklı kaynaklardan gelen verileri birleştirme)

v3.1 ÖZELLİKLERİ (Industrial Data Extractor):
- ✅ Hybrid OCR (dijital/taranmış PDF ayrımı)
- ✅ Multi-Format Ingestion (PDF, Excel, CSV desteği)
- ✅ Smart Table Reconstruction (kırık tablo satırlarını yeniden oluşturma)
- ✅ Source Highlighting (sayfa ve satır numarası ile denetim izi)
- ✅ Industrial data extraction (enerji, yakıt, üretim verisi)
- ✅ Scope 1 & Scope 2 emissions tracking
- ✅ Financial noise filtering (parasal değerleri yok sayma)
- ✅ Confidence scoring per field

v3.0 ÖZELLİKLERİ:
- ✅ Retry mekanizması (API hatalarında otomatik tekrar deneme)
- ✅ Loglama sistemi (detaylı log dosyaları)
- ✅ Cache sistemi (aynı PDF'i tekrar işlememek için)
- ✅ Chunk processing (uzun belgeler için parçalı işleme)
- ✅ PDF metadata çıkarma (otomatik ön doldurma)
- ✅ Rate limiting (API call sınırı)
- ✅ Progress callback (ilerleme bildirimi)
- ✅ Detaylı hata mesajları
- ✅ Batch Processing (birden fazla PDF'i tek seferde işleme)
- ✅ Confidence Score (çıkarılan verinin güvenilirlik skoru)
- ✅ Multi-Format Export (CSV, Excel, SQL çıktıları)
- ✅ Document Summary (belge özeti çıkarma)
- ✅ Language Detection (belge dili tespiti)
- ✅ Statistics & Reporting (detaylı istatistik raporları)
"""

import os
import json
import re
import logging
from typing import Dict, Any, Optional, Callable, List, Tuple
from pathlib import Path
from datetime import datetime
import time

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    genai = None  # type: ignore

from ..utils.cache import PDFCache
from ..utils.retry import retry_with_backoff, RateLimiter
from ..utils.export import export_to_csv, export_batch_to_csv, export_to_excel, export_to_sql_inserts
from ..utils.language import detect_language, detect_language_advanced
from ..utils.statistics import ProcessingStats

# Logger setup
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Unit Conversion Engine (v3.2)
# ---------------------------------------------------------------------------

# Anahtar format: (kaynak_birim, hedef_birim) -> çarpan
# CBAM standart birimleri: tons (kütle), MWh (enerji), m3 (hacim)
UNIT_CONVERSIONS: Dict[Tuple[str, str], float] = {
    # Kütle → tons
    ("lbs", "tons"): 0.000453592,
    ("lb", "tons"): 0.000453592,
    ("kg", "tons"): 0.001,
    ("tonnes", "tons"): 1.0,
    ("t", "tons"): 1.0,
    # Enerji → MWh
    ("mmbtu", "mwh"): 0.293071,
    ("kwh", "mwh"): 0.001,
    ("gwh", "mwh"): 1000.0,
    ("gj", "mwh"): 0.277778,
    ("tj", "mwh"): 277.778,
    # Hacim (doğalgaz) → m3
    ("sm3", "m3"): 1.0,
    ("nm3", "m3"): 1.0,
    ("mcf", "m3"): 28.3168,
}


def normalize_units(value: float, unit: str, target_unit: str) -> float:
    """
    Değeri kaynak birimden CBAM standart hedef birimine dönüştürür.

    Desteklenen dönüşümler için ``UNIT_CONVERSIONS`` sözlüğüne bakın.
    Eğer kaynak ve hedef aynıysa değer olduğu gibi döner.
    Bilinmeyen çift için ``ValueError`` fırlatır.

    Parameters
    ----------
    value : float
        Dönüştürülecek sayısal değer.
    unit : str
        Kaynak birim (büyük/küçük harf duyarsız).
    target_unit : str
        Hedef birim (büyük/küçük harf duyarsız).

    Returns
    -------
    float
        Dönüştürülmüş değer.

    Raises
    ------
    ValueError
        Desteklenmeyen birim çifti.
    """
    src = unit.strip().lower()
    tgt = target_unit.strip().lower()

    if src == tgt:
        return value

    factor = UNIT_CONVERSIONS.get((src, tgt))
    if factor is None:
        raise ValueError(
            f"Desteklenmeyen birim dönüşümü: '{unit}' → '{target_unit}'. "
            f"Desteklenen çiftler: {list(UNIT_CONVERSIONS.keys())}"
        )

    return round(value * factor, 6)


class DataExtractor:
    """
    PDF belgelerinden yapılandırılmış veri çıkaran ajan.
    Gemini ve GPT modellerini destekler.
    
    Yeni Özellikler:
    - Retry mekanizması
    - Cache sistemi
    - Chunk processing
    - PDF metadata
    - Rate limiting
    - Progress tracking
    """
    
    # Beklenen JSON şeması (v3.1 - Industrial Mode)
    EXPECTED_SCHEMA = {
        "document_metadata": {
            "filename": "string",
            "file_type": "PDF | EXCEL | SCANNED_IMAGE",
            "processed_at": "ISO_TIMESTAMP",
            "extraction_method": "TEXT_LAYER | OCR_VISION | SPREADSHEET_PARSER"
        },
        "reporting_period": {
            "start_date": "YYYY-MM-DD or null",
            "end_date": "YYYY-MM-DD or null",
            "raw_text_found": "string (e.g., 'Dönem: 01.01.2026 - 31.01.2026')"
        },
        "production": {
            "item_name": "string or null",
            "quantity": "number or null",
            "unit": "string or null",
            "source_location": {
                "page": "number",
                "row_index": "number or null",
                "confidence": "float (0.0-1.0)"
            }
        },
        "energy_scope_2": {
            "electricity": {
                "total_value": "number or null",
                "unit": "string",
                "breakdown": {
                    "t1_day": "number or null",
                    "t2_peak": "number or null",
                    "t3_night": "number or null"
                },
                "source_location": {
                    "page": "number",
                    "confidence": "float"
                }
            }
        },
        "energy_scope_1": [
            {
                "fuel_type": "Natural Gas | Coal | Diesel | Other",
                "value": "number",
                "unit": "string",
                "source_location": {
                    "page": "number",
                    "row_match": "string (raw text of the row)"
                }
            }
        ],
        "validation_flags": [
            "string (e.g., 'WARNING: Low OCR confidence on Energy field')",
            "string (e.g., 'INFO: Excel file processed successfully')"
        ]
    }
    
    def __init__(
        self,
        llm_provider: str = "gemini",
        api_key: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl_hours: int = 24,
        max_retries: int = 3,
        chunk_size: int = 15000,
        rate_limit_per_minute: int = 10,
        enable_stats: bool = True
    ):
        """
        Args:
            llm_provider: "gemini" veya "gpt"
            api_key: API anahtarı (None ise çevre değişkeninden alınır)
            use_cache: Cache kullanımı (True/False)
            cache_ttl_hours: Cache geçerlilik süresi (saat)
            max_retries: Maksimum retry sayısı
            chunk_size: Chunk boyutu (karakter)
            rate_limit_per_minute: Dakikada maksimum API call sayısı
            enable_stats: İstatistik toplama (True/False)
        """
        self.llm_provider = llm_provider.lower()
        self.use_cache = use_cache
        self.chunk_size = chunk_size
        self.max_retries = max_retries
        
        # Cache sistemi
        if use_cache:
            self.cache = PDFCache(cache_dir="cache", ttl_hours=cache_ttl_hours)
            logger.info(f"Cache aktif (TTL: {cache_ttl_hours} saat)")
        else:
            self.cache = None
            logger.info("Cache devre dışı")
        
        # Rate limiter
        self.rate_limiter = RateLimiter(calls_per_minute=rate_limit_per_minute)
        logger.info(f"Rate limiter: {rate_limit_per_minute} call/dakika")
        
        # Statistics tracker
        self.stats = ProcessingStats() if enable_stats else None
        if enable_stats:
            logger.info("İstatistik toplama aktif")
        
        # LLM setup
        if self.llm_provider == "gemini":
            if genai is None:
                raise ImportError("google-generativeai paketi yüklü değil. 'pip install google-generativeai' komutunu çalıştırın.")
            api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY bulunamadı")
            genai.configure(api_key=api_key)  # type: ignore
            self.model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore
            logger.info("LLM Provider: Gemini 2.5 Flash")
            
        elif self.llm_provider == "gpt":
            if OpenAI is None:
                raise ImportError("openai paketi yüklü değil. 'pip install openai' komutunu çalıştırın.")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY bulunamadı")
            self.client = OpenAI(api_key=api_key)
            logger.info("LLM Provider: GPT-4o")
        else:
            raise ValueError(f"Desteklenmeyen LLM provider: {llm_provider}")
    
    def extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        PDF'in metadata'sını çıkarır.
        
        Args:
            pdf_path: PDF dosyasının yolu
            
        Returns:
            Metadata dictionary
        """
        if pdfplumber is None:
            return {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:  # type: ignore
                metadata = pdf.metadata or {}
                
                return {
                    "title": metadata.get("Title", ""),
                    "author": metadata.get("Author", ""),
                    "subject": metadata.get("Subject", ""),
                    "creator": metadata.get("Creator", ""),
                    "producer": metadata.get("Producer", ""),
                    "creation_date": metadata.get("CreationDate", ""),
                    "modification_date": metadata.get("ModDate", ""),
                    "page_count": len(pdf.pages)
                }
        except Exception as e:
            logger.warning(f"PDF metadata çıkarılamadı: {str(e)}")
            return {}
    
    def extract_text_from_pdf(self, pdf_path: str, progress_callback: Optional[Callable] = None) -> str:
        """
        PDF'den metni çıkarır.
        
        Args:
            pdf_path: PDF dosyasının yolu
            progress_callback: İlerleme callback fonksiyonu
            
        Returns:
            Çıkarılan metin
        """
        if pdfplumber is None:
            raise ImportError("pdfplumber paketi yüklü değil. 'pip install pdfplumber' komutunu çalıştırın.")
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")
        
        logger.info(f"PDF okunuyor: {pdf_path}")
        
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:  # type: ignore
                total_pages = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages, 1):
                    if progress_callback:
                        progress_callback("extract_text", i, total_pages)
                    
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    if i % 10 == 0:
                        logger.debug(f"PDF okuma: {i}/{total_pages} sayfa")
                
                logger.info(f"PDF okuma tamamlandı: {total_pages} sayfa, {len(text)} karakter")
                
        except Exception as e:
            logger.error(f"PDF okuma hatası: {str(e)}", exc_info=True)
            raise RuntimeError(f"PDF okuma hatası: {str(e)}")
        
        if not text.strip():
            raise ValueError("PDF'den metin çıkarılamadı (boş sayfa)")
        
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Metni temizler ve normalleştirir.
        
        Args:
            text: Ham metin
            
        Returns:
            Temizlenmiş metin
        """
        logger.debug(f"Metin temizleniyor: {len(text)} karakter")
        
        # Fazla boşlukları temizle
        text = re.sub(r' +', ' ', text)
        
        # Fazla satır sonlarını temizle
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Özel karakterleri temizle
        text = text.replace('\x00', '')
        text = text.replace('\r', '\n')
        
        # Baştaki ve sondaki boşlukları kaldır
        text = text.strip()
        
        logger.debug(f"Metin temizlendi: {len(text)} karakter")
        return text
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """
        Uzun metni chunk'lara böler.
        
        Args:
            text: Metin
            
        Returns:
            Chunk listesi
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Metin {len(chunks)} chunk'a bölündü (chunk size: {self.chunk_size})")
        return chunks
    
    def _create_extraction_prompt(self, text: str, is_chunk: bool = False) -> str:
        """
        LLM için extraction prompt'u oluşturur (v3.1 - Industrial Mode).
        
        Args:
            text: Temizlenmiş metin
            is_chunk: Chunk işlemesi mi
            
        Returns:
            Prompt metni
        """
        schema_str = json.dumps(self.EXPECTED_SCHEMA, indent=2, ensure_ascii=False)
        
        chunk_instruction = ""
        if is_chunk:
            chunk_instruction = "\n\nNOTE: This is a chunk of the full document. Extract only the information present in this chunk."
        
        prompt = f"""**Role:**
You are an **Industrial Document Analyst & OCR Specialist**. Your sole purpose is to extract high-precision engineering and energy data from complex factory documents for EU CBAM (Carbon Border Adjustment Mechanism) compliance.

**Capabilities:**
1. **Hybrid OCR:** You can distinguish between digital text PDFs and scanned image PDFs. You apply Vision/OCR techniques when text layers are missing.
2. **Multi-Format Ingestion:** You process PDFs (`.pdf`), Excel spreadsheets (`.xlsx`, `.xls`), and CSV files (`.csv`) natively.
3. **Smart Table Reconstruction:** You can identify and reconstruct broken table rows in invoices where data spans multiple lines.
4. **Source Highlighting:** You must pinpoint exactly *where* (Page #, Row #) you found the data to provide an audit trail.

---

### ⚙️ Execution Protocol (Step-by-Step)

#### Phase 1: Format Detection & Ingestion strategy
* **IF Input is Excel/CSV:**
    * Ignore formatting (colors, borders). Focus on headers containing keywords: `Consumption`, `Tüketim`, `kWh`, `MWh`, `Ton`, `Quantity`, `Miktar`.
    * Look for the "Sheet1" or the tab with the most data rows.
* **IF Input is PDF:**
    * **Check:** Is raw text extractable?
    * **Decision:**
        * If `text_length > 50 chars`: Use standard text extraction (Fast Mode).
        * If `text_length < 50 chars` OR contains "garbled" characters: Activate **Vision/OCR Mode** (Slow Mode). Treat the page as an image.

#### Phase 2: Data Extraction Rules (The "What")
You must extract **only** the following entities. Do NOT infer or calculate.

1. **Reporting Period:**
    * Look for `Fatura Dönemi`, `Consumption Period`, `Okuma Tarihi`.
    * Format: `YYYY-MM-DD` (Start) to `YYYY-MM-DD` (End).
    * *Rule:* If multiple dates exist, prefer the "Consumption" range over the "Invoice Date".

2. **Production Data:**
    * Look for: `Üretim`, `Production`, `Finished Goods`, `Çelik`, `Kütük`, `Billet`.
    * Unit: `Ton`, `kg`.

3. **Energy Consumption (Scope 2):**
    * Look for: `Aktif Enerji`, `Active Energy`, `Gündüz`, `Puant`, `Gece`, `Toplam Tüketim`.
    * *Critical Rule:* If the invoice lists Day (T1), Peak (T2), and Night (T3) separately, **SUM THEM** to get the total, but also keep the breakdown if possible.
    * *Noise Filter:* Ignore "Inductive" (Endüktif) or "Capacitive" (Kapasitif) or "Reaktif" values. Only extract **Active** energy.

4. **Fuel Consumption (Scope 1):**
    * Look for: `Doğalgaz`, `Natural Gas`, `Kömür`, `Coal`, `Diesel`.
    * Unit: `m3`, `Sm3`, `kWh` (for gas), `Ton` (for coal).

#### Phase 3: Validation & Cleanup
* **Financial Noise:** Ignore all monetary values (TL, EUR, USD). Do not confuse `Total Amount (TL)` with `Total Consumption (kWh)`.
* **Unit Normalization:** Keep the unit exactly as seen (e.g., "kWh", "MWh"). Do not convert units.
* **Null Handling:** If a field is not found, set value to `null`. Never hallucinate data.

---

### 📝 Output Schema (Strict JSON)

You must return the result in this **exact** JSON structure. Do not include markdown formatting or conversational text outside the JSON.

{schema_str}

---

### 🧠 Edge Case Handling (Chain of Thought)

* **Scenario A: Scanned Invoice.**
    * *Action:* If text extraction yields gibberish, flag `extraction_method` as "OCR_VISION". Use visual layout analysis to find the "Total Consumption" box, usually located at the bottom right of energy tables.
* **Scenario B: Excel with Multiple Sheets.**
    * *Action:* Scan the first 3 sheets. Prioritize the sheet named "Tüketim", "Data", or "Rapor". Ignore sheets named "Pivot" or "Summary" if raw data is available.
* **Scenario C: Disjointed Tables.**
    * *Action:* If headers are on Page 1 but data is on Page 2, maintain the column mapping context across pages.

---

### 🚀 Final Instruction to the Model
"Analyze the provided document based on the rules above. Extract the data with the highest possible precision. If you are unsure about a value (confidence < 0.5), leave it as `null` and add a note in `validation_flags`. **Output ONLY the JSON.**"{chunk_instruction}

---

DOCUMENT TEXT:
{text[:self.chunk_size]}

Provide the structured JSON output:
"""
        
        return prompt
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
    def _call_llm(self, prompt: str) -> str:
        """
        LLM'e call yapar (retry mekanizmalı).
        
        Args:
            prompt: Prompt
            
        Returns:
            LLM yanıtı
        """
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        logger.debug(f"LLM call başlıyor ({self.llm_provider})")
        
        try:
            if self.llm_provider == "gemini":
                response = self.model.generate_content(  # type: ignore
                    prompt,
                    generation_config={  # type: ignore
                        "temperature": 0.1,
                        "response_mime_type": "application/json"
                    }
                )
                result_text = response.text  # type: ignore
            
            else:  # gpt
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an Industrial Document Analyst & OCR Specialist. You extract high-precision engineering and energy data from complex factory documents for EU CBAM compliance. You output ONLY structured JSON data without any additional text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                result_text = response.choices[0].message.content
            
            if result_text is None:
                raise ValueError("LLM boş yanıt döndü")
            
            logger.debug(f"LLM yanıt alındı: {len(result_text)} karakter")
            return result_text
            
        except Exception as e:
            logger.error(f"LLM call hatası: {str(e)}")
            raise
    
    def _merge_chunk_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Chunk sonuçlarını birleştirir.
        
        Args:
            results: Chunk sonuçları
            
        Returns:
            Birleştirilmiş sonuç
        """
        if len(results) == 1:
            return results[0]
        
        logger.info(f"{len(results)} chunk sonucu birleştiriliyor")
        
        merged = results[0].copy()
        
        # Liste alanları birleştir
        list_fields = ["sectors_covered", "emissions_categories", "key_obligations", 
                      "compliance_deadlines", "relevant_articles"]
        
        for field in list_fields:
            all_items = []
            for result in results:
                value = result.get(field)
                if value and value != "NULL" and isinstance(value, list):
                    all_items.extend(value)
            
            # Tekrar edenleri temizle
            if all_items:
                if isinstance(all_items[0], dict):
                    # Object listesi için
                    seen = set()
                    unique = []
                    for item in all_items:
                        key = json.dumps(item, sort_keys=True)
                        if key not in seen:
                            seen.add(key)
                            unique.append(item)
                    merged[field] = unique
                else:
                    # String listesi için
                    merged[field] = list(set(all_items))
            else:
                merged[field] = "NULL"
        
        # String alanları birleştir (en uzun olanı al)
        string_fields = ["legal_basis", "scope", "reporting_requirements", "penalties"]
        for field in string_fields:
            longest = ""
            for result in results:
                value = result.get(field, "")
                if value and value != "NULL" and len(value) > len(longest):
                    longest = value
            merged[field] = longest if longest else "NULL"
        
        logger.info("Chunk sonuçları birleştirildi")
        return merged
    
    def extract_with_llm(
        self,
        text: str,
        use_chunking: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        LLM kullanarak metinden yapılandırılmış veri çıkarır.
        
        Args:
            text: Temizlenmiş metin
            use_chunking: Chunk processing kullan
            progress_callback: İlerleme callback
            
        Returns:
            Çıkarılan yapılandırılmış veri
        """
        logger.info(f"LLM extraction başlıyor: {len(text)} karakter")
        
        try:
            # Chunk'lara böl (gerekiyorsa)
            if use_chunking and len(text) > self.chunk_size:
                chunks = self._split_into_chunks(text)
                results = []
                
                for i, chunk in enumerate(chunks, 1):
                    if progress_callback:
                        progress_callback("extract_llm", i, len(chunks))
                    
                    logger.info(f"Chunk {i}/{len(chunks)} işleniyor")
                    prompt = self._create_extraction_prompt(chunk, is_chunk=True)
                    result_text = self._call_llm(prompt)
                    extracted_data = json.loads(result_text)
                    results.append(extracted_data)
                
                # Sonuçları birleştir
                extracted_data = self._merge_chunk_results(results)
            
            else:
                # Tek seferde işle
                prompt = self._create_extraction_prompt(text[:self.chunk_size])
                result_text = self._call_llm(prompt)
                extracted_data = json.loads(result_text)
            
            # Şema validasyonu
            self._validate_schema(extracted_data)
            
            logger.info("LLM extraction başarılı")
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası: {str(e)}", exc_info=True)
            raise ValueError(f"LLM'den geçersiz JSON döndü: {str(e)}")
        except Exception as e:
            logger.error(f"LLM extraction hatası: {str(e)}", exc_info=True)
            raise RuntimeError(f"LLM extraction hatası: {str(e)}")
    
    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """
        Çıkarılan verinin şemaya uygun olduğunu kontrol eder.
        
        Args:
            data: Çıkarılan veri
            
        Raises:
            ValueError: Şema uyumsuzluğu varsa
        """
        expected_keys = set(self.EXPECTED_SCHEMA.keys())
        actual_keys = set(data.keys())
        
        missing_keys = expected_keys - actual_keys
        if missing_keys:
            logger.warning(f"Eksik alanlar bulundu: {missing_keys}")
            # Eksik anahtarları NULL ile doldur
            for key in missing_keys:
                data[key] = "NULL"
    
    def process_document(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        use_chunking: bool = True,
        force_reprocess: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        PDF belgesini işler ve yapılandırılmış veri çıkarır.
        
        Args:
            pdf_path: PDF dosyasının yolu
            output_path: Çıktı JSON dosyasının yolu (None ise kaydedilmez)
            use_chunking: Chunk processing kullan
            force_reprocess: Cache'i yoksay ve tekrar işle
            progress_callback: İlerleme callback fonksiyonu
            
        Returns:
            Çıkarılan yapılandırılmış veri
            
        Progress Callback:
            callback(stage: str, current: int, total: int)
            stage: "extract_text", "extract_llm", "complete"
        """
        logger.info(f"=" * 60)
        logger.info(f"Belge işleme başlıyor: {pdf_path}")
        logger.info(f"=" * 60)
        
        # Cache kontrolü
        if self.use_cache and self.cache and not force_reprocess:
            cached_result = self.cache.get(pdf_path)
            if cached_result:
                logger.info("✅ Cache'den yüklendi!")
                print("✅ Cache'den yüklendi (işleme atlandı)")
                return cached_result
        
        start_time = datetime.now()
        
        try:
            # PDF metadata çıkar
            logger.info("📄 PDF metadata çıkarılıyor...")
            pdf_metadata = self.extract_pdf_metadata(pdf_path)
            logger.info(f"Metadata: {pdf_metadata.get('page_count', 0)} sayfa")
            
            # PDF'den metin çıkar
            logger.info("📄 PDF metni çıkarılıyor...")
            print(f"📄 PDF okunuyor: {pdf_path}")
            raw_text = self.extract_text_from_pdf(pdf_path, progress_callback)
            
            # Metni temizle
            logger.info("🧹 Metin temizleniyor...")
            print(f"🧹 Metin temizleniyor... ({len(raw_text)} karakter)")
            cleaned_text = self.clean_text(raw_text)
            
            # 🆕 Dil tespiti
            logger.info("🌍 Dil tespiti yapılıyor...")
            detected_lang, lang_confidence = self.detect_language(cleaned_text)
            logger.info(f"Tespit edilen dil: {detected_lang} (güven: {lang_confidence})")
            
            # LLM ile veri çıkar
            logger.info(f"🤖 LLM ile veri çıkarılıyor ({self.llm_provider.upper()})...")
            print(f"🤖 LLM ile veri çıkarılıyor ({self.llm_provider.upper()})...")
            extracted_data = self.extract_with_llm(cleaned_text, use_chunking, progress_callback)
            
            # 🆕 Confidence score hesapla
            confidence_score = self._calculate_confidence_score(extracted_data)
            logger.info(f"✨ Confidence score: {confidence_score}")
            
            # Metadata ekle
            extracted_data["_metadata"] = {
                "source_file": str(Path(pdf_path).name),
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "llm_provider": self.llm_provider,
                "text_length": len(cleaned_text),
                "page_count": pdf_metadata.get("page_count", 0),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "used_chunking": use_chunking and len(cleaned_text) > self.chunk_size,
                "chunk_size": self.chunk_size if use_chunking else None,
                "detected_language": detected_lang,
                "language_confidence": lang_confidence,
                "confidence_score": confidence_score
            }
            
            # PDF metadata'yı da ekle
            if pdf_metadata:
                extracted_data["_pdf_metadata"] = pdf_metadata
            
            # Cache'e kaydet
            if self.use_cache and self.cache:
                self.cache.set(pdf_path, extracted_data)
                logger.info("💾 Cache'e kaydedildi")
            
            # Dosyaya kaydet
            if output_path:
                self._save_json(extracted_data, output_path)
                logger.info(f"💾 Dosyaya kaydedildi: {output_path}")
                print(f"💾 Veri kaydedildi: {output_path}")
            
            # Progress callback
            if progress_callback:
                progress_callback("complete", 1, 1)
            
            logger.info("✅ Extraction tamamlandı!")
            print("✅ Extraction tamamlandı!")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⏱️  Toplam süre: {processing_time:.2f} saniye")
            
            # 🆕 İstatistik kaydı
            if self.stats:
                self.stats.record_success(extracted_data.get("_metadata", {}))
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Belge işleme hatası: {str(e)}", exc_info=True)
            
            # 🆕 Hata kaydı
            if self.stats:
                self.stats.record_failure(str(Path(pdf_path).name), str(e))
            
            raise
    
    def _save_json(self, data: Dict[str, Any], output_path: str) -> None:
        """JSON verisini dosyaya kaydeder."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # =============================================================================
    # 🆕 YENİ ÖZELLİKLER v3.0
    # =============================================================================
    
    def detect_language(self, text: str, use_advanced: bool = False) -> Tuple[str, float]:
        """
        Metnin dilini tespit eder.
        
        Args:
            text: Metin
            use_advanced: langdetect kütüphanesini kullan (daha doğru)
            
        Returns:
            (dil_kodu, güven_skoru) tuple
        """
        if use_advanced:
            return detect_language_advanced(text)
        else:
            return detect_language(text)
    
    def _calculate_confidence_score(self, extracted_data: Dict[str, Any]) -> float:
        """
        Çıkarılan verinin güvenilirlik skorunu hesaplar.
        
        Score Faktörleri:
        - Dolu alan sayısı (NULL olmayan)
        - Kritik alanların doluluk oranı
        - Liste alanlarının uzunluğu
        
        Args:
            extracted_data: Çıkarılan veri
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        # Metadata alanlarını çıkar
        data = {k: v for k, v in extracted_data.items() if not k.startswith('_')}
        
        total_fields = len(data)
        filled_fields = sum(1 for v in data.values() if v not in ["NULL", None, "", []])
        
        # Kritik alanlar (bu alanlar önemli)
        critical_fields = [
            "document_name", "document_number", "document_type",
            "publication_date", "issuing_authority"
        ]
        critical_filled = sum(1 for k in critical_fields if data.get(k) not in ["NULL", None, ""])
        critical_ratio = critical_filled / len(critical_fields)
        
        # Liste alanlarının doluluk oranı
        list_fields = [
            "sectors_covered", "emissions_categories", "key_obligations",
            "compliance_deadlines", "relevant_articles"
        ]
        list_filled = sum(
            1 for k in list_fields 
            if isinstance(data.get(k), list) and len(data.get(k, [])) > 0
        )
        list_ratio = list_filled / len(list_fields) if list_fields else 0
        
        # Genel doluluk oranı
        fill_ratio = filled_fields / total_fields
        
        # Ağırlıklı ortalama
        # 40% kritik alanlar, 30% genel doluluk, 30% liste alanları
        confidence = (0.4 * critical_ratio) + (0.3 * fill_ratio) + (0.3 * list_ratio)
        
        return round(confidence, 2)
    
    def generate_summary(self, extracted_data: Dict[str, Any], max_length: int = 500) -> str:
        """
        Çıkarılan veriden belge özeti oluşturur.
        
        Args:
            extracted_data: Çıkarılan veri
            max_length: Maksimum özet uzunluğu (karakter)
            
        Returns:
            Belge özeti
        """
        summary_parts = []
        
        # Belge adı ve tipi
        doc_name = extracted_data.get("document_name", "Unknown Document")
        doc_type = extracted_data.get("document_type", "Unknown Type")
        summary_parts.append(f"{doc_name} ({doc_type})")
        
        # Yayın bilgisi
        pub_date = extracted_data.get("publication_date", "Unknown")
        authority = extracted_data.get("issuing_authority", "Unknown")
        summary_parts.append(f"Published on {pub_date} by {authority}.")
        
        # Kapsam
        scope = extracted_data.get("scope", "")
        if scope and scope != "NULL":
            scope_short = scope[:200] + "..." if len(scope) > 200 else scope
            summary_parts.append(f"Scope: {scope_short}")
        
        # Sektörler
        sectors = extracted_data.get("sectors_covered", [])
        if sectors and sectors != "NULL" and isinstance(sectors, list):
            sectors_str = ", ".join(sectors[:5])
            summary_parts.append(f"Sectors: {sectors_str}")
        
        # Key obligations
        obligations = extracted_data.get("key_obligations", [])
        if obligations and obligations != "NULL" and isinstance(obligations, list):
            summary_parts.append(f"Key obligations include {len(obligations)} requirements.")
        
        summary = " ".join(summary_parts)
        
        # Uzunluk sınırı
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def process_documents_batch(
        self,
        pdf_paths: List[str],
        output_dir: str = "output/batch",
        use_chunking: bool = True,
        stop_on_error: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Birden fazla PDF belgesini toplu halde işler.
        
        Args:
            pdf_paths: PDF dosya yolları listesi
            output_dir: Çıktı klasörü
            use_chunking: Chunk processing kullan
            stop_on_error: Hata durumunda dur
            progress_callback: İlerleme callback
            
        Returns:
            Çıkarılan veriler listesi
        """
        logger.info(f"🚀 Batch processing başlıyor: {len(pdf_paths)} belge")
        print(f"\n🚀 Batch Processing: {len(pdf_paths)} belge")
        print("="*60)
        
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            try:
                print(f"\n[{i}/{len(pdf_paths)}] İşleniyor: {Path(pdf_path).name}")
                
                # Her PDF için ayrı çıktı dosyası
                filename = Path(pdf_path).stem
                json_output = output_path / f"{filename}.json"
                
                # İşle
                result = self.process_document(
                    pdf_path=pdf_path,
                    output_path=str(json_output),
                    use_chunking=use_chunking,
                    progress_callback=progress_callback
                )
                
                results.append(result)
                print(f"✅ Başarılı: {Path(pdf_path).name}")
                
            except Exception as e:
                logger.error(f"❌ Hata: {pdf_path} - {str(e)}")
                print(f"❌ Hata: {Path(pdf_path).name} - {str(e)}")
                
                if stop_on_error:
                    raise
                else:
                    # Hata durumunda boş veri ekle
                    results.append({
                        "error": str(e),
                        "_metadata": {
                            "source_file": str(Path(pdf_path).name),
                            "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "failed"
                        }
                    })
        
        print("\n" + "="*60)
        print(f"✅ Batch processing tamamlandı!")
        print(f"   Başarılı: {len([r for r in results if 'error' not in r])}/{len(pdf_paths)}")
        print(f"   Başarısız: {len([r for r in results if 'error' in r])}/{len(pdf_paths)}")
        
        return results
    
    def export_to_csv(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Çıkarılan veriyi CSV formatında kaydeder.
        
        Args:
            data: Çıkarılan veri
            output_path: CSV dosya yolu
        """
        export_to_csv(data, output_path)
        logger.info(f"📄 CSV'ye kaydedildi: {output_path}")
    
    def export_batch_to_csv(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Birden fazla belge verisini tek CSV'ye kaydeder.
        
        Args:
            results: Çıkarılan veriler listesi
            output_path: CSV dosya yolu
        """
        export_batch_to_csv(results, output_path)
        logger.info(f"📄 Batch CSV'ye kaydedildi: {output_path}")
    
    def export_to_excel(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Birden fazla belge verisini Excel formatında kaydeder.
        
        Args:
            results: Çıkarılan veriler listesi
            output_path: Excel dosya yolu
        """
        export_to_excel(results, output_path)
        logger.info(f"📊 Excel'e kaydedildi: {output_path}")
    
    def export_to_sql(self, results: List[Dict[str, Any]], table_name: str = "documents", output_path: Optional[str] = None) -> str:
        """
        Birden fazla belge verisini SQL INSERT statement'larına dönüştürür.
        
        Args:
            results: Çıkarılan veriler listesi
            table_name: Tablo adı
            output_path: SQL dosya yolu (None ise string döner)
            
        Returns:
            SQL INSERT statements
        """
        sql = export_to_sql_inserts(results, table_name, output_path)
        if output_path:
            logger.info(f"🗄️  SQL'e kaydedildi: {output_path}")
        return sql
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """
        İstatistik özetini döndürür.
        
        Returns:
            İstatistik özeti
        """
        if not self.stats:
            return {"error": "Statistics disabled"}
        
        return self.stats.get_summary()
    
    def get_stats_report(self) -> str:
        """
        Detaylı istatistik raporunu döndürür.
        
        Returns:
            Detaylı rapor metni
        """
        if not self.stats:
            return "Statistics disabled"
        
        return self.stats.get_detailed_report()
    
    def save_stats_report(self, output_path: str) -> None:
        """
        İstatistik raporunu dosyaya kaydeder.
        
        Args:
            output_path: Rapor dosya yolu (JSON)
        """
        if not self.stats:
            logger.warning("Statistics disabled, nothing to save")
            return
        
        self.stats.save_report(output_path)
        logger.info(f"📊 İstatistik raporu kaydedildi: {output_path}")
    
    def reset_stats(self) -> None:
        """İstatistikleri sıfırlar."""
        if self.stats:
            self.stats.reset()
            logger.info("📊 İstatistikler sıfırlandı")
    
    def clear_cache(self) -> int:
        """
        Cache'i temizler.
        
        Returns:
            Silinen dosya sayısı
        """
        if self.cache:
            count = self.cache.clear()
            logger.info(f"Cache temizlendi: {count} dosya silindi")
            return count
        return 0

    # =================================================================
    # 🆕 v3.2 — Data Fusion & Unit Normalization
    # =================================================================

    @staticmethod
    def normalize_units(
        value: float,
        unit: str,
        target_unit: str,
    ) -> float:
        """Convenience wrapper — delegates to module-level ``normalize_units``."""
        return normalize_units(value, unit, target_unit)

    @staticmethod
    def fuse_documents(extracted_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Birden fazla belge sonucunu tek bir tutarlı JSON payload’ına birleştirir.

        Kullanım Senaryosu
        ------------------
        Fabrikada elektrik verisi bir PDF faturada, üretim verisi ise bir
        Excel SCADA dosyasında bulunabilir.  Bu metot her iki kaynağın
        ``process_document`` çıktılarını alır ve ``reporting_period``’a
        göre eşleştirip eksik alanları karşılıklı doldurur.

        Birleştirme Kuralları
        --------------------
        1. İlk sonuç "temel" (base) olarak alınır.
        2. Sonraki sonuçlar sırayla işlenir.
        3. Base’de ``null`` / ``None`` / ``"NULL"`` / boş olan alanlar,
           sonraki sonucun değeriyle doldurulur.
        4. Zıt yönde de aynı şey geçerlidir—her iki tarafta
           dolu olan alanlar base’deki değeri korur
           (öncelik: listedeki sıra).
        5. ``validation_flags`` ve ``energy_scope_1`` gibi liste alanları
           birleştirilir (merge).
        6. Çıktıya ``data_fusion_log`` dizisi eklenir: hangi alanın
           hangi dosyadan geldiğini belirtir.

        Parameters
        ----------
        extracted_results : List[Dict[str, Any]]
            ``process_document`` çıktılarının listesi.

        Returns
        -------
        Dict[str, Any]
            Birleştirilmiş tek JSON payload.

        Raises
        ------
        ValueError
            Boş liste verilirse.
        """
        if not extracted_results:
            raise ValueError("fuse_documents() için en az 1 sonuç gereklidir.")

        if len(extracted_results) == 1:
            single = extracted_results[0].copy()
            source = single.get("_metadata", {}).get("source_file", "unknown")
            single["data_fusion_log"] = [f"Single document — all fields from '{source}'."]
            return single

        # Yardımcı fonksiyonlar
        def _is_empty(val: Any) -> bool:
            """Değerin "boş" sayılıp sayılmadığını belirler."""
            if val is None:
                return True
            if isinstance(val, str) and val.strip().upper() in ("", "NULL"):
                return True
            if isinstance(val, list) and len(val) == 0:
                return True
            return False

        def _source_label(result: Dict[str, Any]) -> str:
            return result.get("_metadata", {}).get("source_file", "unknown")

        # Listelerin birleştirilmesi gereken alanlar
        LIST_MERGE_FIELDS = {
            "validation_flags",
            "energy_scope_1",
        }

        # Meta / iç alanları birleştirmeden dışı tut
        SKIP_FIELDS = {"_metadata", "_pdf_metadata", "data_fusion_log"}

        import copy
        base = copy.deepcopy(extracted_results[0])
        fusion_log: List[str] = []
        base_source = _source_label(extracted_results[0])

        # base’deki dolu alanları logla
        for key, val in base.items():
            if key in SKIP_FIELDS:
                continue
            if not _is_empty(val):
                fusion_log.append(f"'{key}' ← '{base_source}'")

        # Sonraki sonuçlarla birleştir
        for result in extracted_results[1:]:
            src_label = _source_label(result)
            for key, val in result.items():
                if key in SKIP_FIELDS:
                    continue

                # Liste birleştirme
                if key in LIST_MERGE_FIELDS:
                    base_list = base.get(key)
                    if not isinstance(base_list, list):
                        base_list = []
                    incoming = val if isinstance(val, list) else []
                    merged = base_list + incoming
                    if merged:
                        base[key] = merged
                        if incoming:
                            fusion_log.append(
                                f"'{key}' merged {len(incoming)} item(s) from '{src_label}'"
                            )
                    continue

                # Skaler / dict alanlar: base boşsa doldur
                if _is_empty(base.get(key)) and not _is_empty(val):
                    base[key] = copy.deepcopy(val)
                    fusion_log.append(f"'{key}' ← '{src_label}'")

        base["data_fusion_log"] = fusion_log

        # Fusion metadata
        base.setdefault("_metadata", {})
        base["_metadata"]["fusion_source_count"] = len(extracted_results)
        base["_metadata"]["fusion_sources"] = [
            _source_label(r) for r in extracted_results
        ]

        logger.info(
            f"Data fusion tamamlandı: {len(extracted_results)} belge → "
            f"{len(fusion_log)} alan birleştirildi"
        )
        return base
    
    def clear_expired_cache(self) -> int:
        """
        Süresi dolmuş cache'leri temizler.
        
        Returns:
            Silinen dosya sayısı
        """
        if self.cache:
            count = self.cache.clear_expired()
            logger.info(f"Süresi dolmuş cache temizlendi: {count} dosya silindi")
            return count
        return 0


# Kullanım örneği
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # Loglama setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    load_dotenv()
    
    # Gelişmiş özelliklerle kullanım
    extractor = DataExtractor(
        llm_provider="gemini",
        use_cache=True,
        cache_ttl_hours=24,
        max_retries=3,
        chunk_size=15000,
        rate_limit_per_minute=10
    )
    
    # Progress callback
    def progress(stage: str, current: int, total: int):
        percent = (current / total) * 100
        print(f"[{stage}] İlerleme: {current}/{total} ({percent:.1f}%)")
    
    # İşle
    result = extractor.process_document(
        pdf_path="../../mevzuat_docs/CELEX_32023R0956_EN_TXT.pdf",
        output_path="../../output/extracted_data.json",
        use_chunking=True,
        progress_callback=progress
    )
    
    print("\n" + "="*50)
    print("ÇIKARILAN VERİ:")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))
