"""
Basit kullanım örneği - YENİ ÖZELLİKLER ile
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# .env dosyasını yükle
load_dotenv()

# Proje kök dizinini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.data_extractor import DataExtractor

# Loglama (opsiyonel)
logging.basicConfig(level=logging.INFO)

# 1. Data Extractor oluştur (YENİ ÖZELLİKLER ile)
extractor = DataExtractor(
    llm_provider="gemini",
    use_cache=True,          # ✅ Cache aktif
    cache_ttl_hours=24,      # ✅ 24 saat geçerli
    max_retries=3,           # ✅ 3 kez tekrar dene
    chunk_size=15000,        # ✅ Chunk boyutu
    rate_limit_per_minute=10 # ✅ Rate limiting
)

# 2. PDF'i işle
pdf_path = Path(__file__).parent.parent / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf"
output_path = Path(__file__).parent.parent / "output" / "cbam_data.json"

# Progress callback (opsiyonel)
def show_progress(stage: str, current: int, total: int):
    percent = (current / total) * 100
    print(f"  [{stage}] {current}/{total} ({percent:.0f}%)")

result = extractor.process_document(
    pdf_path=str(pdf_path),
    output_path=str(output_path),
    use_chunking=True,        # ✅ Uzun belgeler için chunk'lama
    force_reprocess=False,    # ✅ Cache kullan (True ise yoksay)
    progress_callback=show_progress  # ✅ İlerleme göster
)

# 3. Sonuçları yazdır
print("\n" + "="*50)
print("📄 Belge:", result['document_name'])
print("📅 Tarih:", result['publication_date'])
print("🏢 Kurum:", result['issuing_authority'])
print("⏱️  Süre:", result['_metadata']['processing_time_seconds'], "saniye")
print("📦 Chunk kullanıldı mı?:", result['_metadata']['used_chunking'])
print("="*50)
