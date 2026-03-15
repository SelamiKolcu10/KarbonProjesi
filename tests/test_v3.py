"""
Hızlı v3.0 test scripti
"""

import sys
# type stubs için uyarıyı göz ardı et (Pylance)
sys.stdout.reconfigure(encoding='utf-8') # type: ignore
sys.stderr.reconfigure(encoding='utf-8') # type: ignore
from pathlib import Path

# Mevcut dizini kullan (test klasörünün bir üstü, projenin kök dizinidir)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.data_extractor import DataExtractor
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DATA EXTRACTOR v3.0 - QUICK TEST")
print("=" * 60)

# Extractor oluştur
extractor = DataExtractor(
    llm_provider="gemini",
    use_cache=True,
    enable_stats=True
)

# 1. Tek belge işle
print("\n1️⃣ Processing single document...")
pdf_path = project_root / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf"

if pdf_path.exists():
    result = extractor.process_document(str(pdf_path), force_reprocess=True)  # Cache'i yoksay
    
    # Yeni metadata bilgileri
    print(f"\n✨ Confidence Score: {result['_metadata']['confidence_score']}")
    print(f"🌍 Language: {result['_metadata']['detected_language']} ({result['_metadata']['language_confidence']})")
    
    # Summary
    summary = extractor.generate_summary(result, max_length=200)
    print(f"\n📝 Summary:\n{summary}")
    
    # 2. Export test
    print("\n2️⃣ Testing exports...")
    extractor.export_to_csv(result, "output/test_v3/single.csv")
    print("✅ CSV exported")
    
    # 3. Stats
    print("\n3️⃣ Statistics:")
    stats = extractor.get_stats_summary()
    print(f"   Processed: {stats['total_processed']}")
    print(f"   Success Rate: {stats['success_rate']}%")
    print(f"   Confidence Score: {result['_metadata']['confidence_score']}")
    
    print("\n✅ v3.0 test tamamlandı!")
else:
    print(f"❌ PDF bulunamadı: {pdf_path}")
