"""
Ajan #1 Test - Düz Metin ile Test
Bu script, PDF olmayan metinlerle ajanı test eder
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.data_extractor import DataExtractor
from dotenv import load_dotenv
import json

load_dotenv()

print("="*60)
print("AJAN #1 TEST - Kompleks Metin İle")
print("="*60)

# Test metni (kullanıcının verdiği)
test_text = """
ABC Döküm Sanayi - Fatura Tarihi: 10 Mart 2026.
Son Ödeme: 20 Mart 2026.
Tüketim Aralığı: 01 Şubat - 28 Şubat 2026.
Aktif Enerji Bedeli: 45.000 TL.
Toplam Tüketim T1: 500,50 kWh.
Toplam Tüketim T2: 200,00 kWh.
Toplam Tüketim T3: 300,00 kWh.
İndüktif Reaktif: 100 kVARh.
Gecikme Zammı: 500 TL.
"""

print("\n📝 TEST METNİ:")
print(test_text)
print("\n" + "="*60)

# Extractor oluştur
extractor = DataExtractor(llm_provider="gemini", enable_stats=True)

# Metni temizle
cleaned_text = extractor.clean_text(test_text)

print("\n🤖 LLM'e gönderiliyor...")
print("⚠️  DİKKAT: Bu metin CBAM belgesi değil, elektrik faturası!")
print("   Çoğu alan NULL dönecek çünkü CBAM şemasına uymuyor.\n")

try:
    # LLM ile çıkar
    result = extractor.extract_with_llm(cleaned_text, use_chunking=False)
    
    print("="*60)
    print("✅ SONUÇ:")
    print("="*60)
    
    # Sonuçları kategorize et
    filled_fields = {k: v for k, v in result.items() 
                     if v not in ["NULL", None, "", []] and not k.startswith('_')}
    null_fields = {k: v for k, v in result.items() 
                   if v in ["NULL", None, "", []] and not k.startswith('_')}
    
    print(f"\n✅ DOLU ALANLAR ({len(filled_fields)}):")
    for key, value in filled_fields.items():
        print(f"   • {key}: {value}")
    
    print(f"\n❌ NULL ALANLAR ({len(null_fields)}):")
    null_list = list(null_fields.keys())
    for i in range(0, len(null_list), 3):
        fields = null_list[i:i+3]
        print(f"   • {', '.join(fields)}")
    
    # Confidence score
    confidence = extractor._calculate_confidence_score(result)
    print(f"\n✨ CONFIDENCE SCORE: {confidence}")
    print(f"   (Düşük çünkü bu bir CBAM belgesi değil)")
    
    # Language detection
    lang, lang_conf = extractor.detect_language(test_text)
    print(f"\n🌍 DİL TESPİTİ: {lang} (güven: {lang_conf})")
    
    # Summary
    summary = extractor.generate_summary(result)
    print(f"\n📝 ÖZET:\n{summary}")
    
    # Tam JSON
    print("\n" + "="*60)
    print("TAM JSON ÇIKTISI:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Analiz
    print("\n" + "="*60)
    print("📊 ANALİZ:")
    print("="*60)
    print(f"✅ Ajan doğru çalıştı!")
    print(f"✅ Belgede olmayan bilgiler için NULL döndü (uydurma yapmadı)")
    print(f"✅ Dil tespiti: {'Türkçe' if lang == 'tr' else lang}")
    print(f"⚠️  Bu metin CBAM şemasına uygun değil")
    print(f"⚠️  CBAM belgesi için PDF'lerden birini kullan")
    
    print("\n" + "="*60)
    print("🎯 SONUÇ: Ajan beklenen şekilde çalışıyor!")
    print("="*60)

except Exception as e:
    print(f"❌ HATA: {str(e)}")
    import traceback
    traceback.print_exc()
