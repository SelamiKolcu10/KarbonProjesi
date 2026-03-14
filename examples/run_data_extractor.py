#!/usr/bin/env python3
"""
Data Extractor kullanım örneği
"""

import sys
import json
from pathlib import Path

# Proje kök dizinini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.data_extractor import DataExtractor
from src.config import Config
from src.utils.logger import setup_logger


def main():
    """Ana fonksiyon"""
    
    # Logger oluştur
    logger = setup_logger("data_extractor_example")
    
    try:
        # Konfigürasyonu doğrula
        logger.info("Konfigürasyon kontrol ediliyor...")
        Config.validate()
        
        # Data Extractor oluştur (YENİ ÖZELLİKLERLE)
        logger.info(f"Data Extractor oluşturuluyor (Provider: {Config.DEFAULT_LLM_PROVIDER})...")
        extractor = DataExtractor(
            llm_provider=Config.DEFAULT_LLM_PROVIDER,
            api_key=Config.get_api_key(Config.DEFAULT_LLM_PROVIDER),
            use_cache=True,
            cache_ttl_hours=24,
            max_retries=3,
            chunk_size=15000,
            rate_limit_per_minute=10
        )
        
        # İşlenecek PDF
        pdf_path = Config.MEVZUAT_DOCS_DIR / "CELEX_32023R0956_EN_TXT.pdf"
        
        if not pdf_path.exists():
            logger.error(f"PDF dosyası bulunamadı: {pdf_path}")
            print("\n⚠️  Lütfen mevzuat_docs/ klasörüne PDF dosyası ekleyin.")
            return
        
        # Çıktı dosyası
        output_path = Config.OUTPUT_DIR / "extracted_cbam_regulation.json"
        
        # Belgeyi işle
        logger.info(f"Belge işleniyor: {pdf_path.name}")
        print("\n" + "="*70)
        print(f"📋 İşlenen Belge: {pdf_path.name}")
        print("="*70)
        
        result = extractor.process_document(
            pdf_path=str(pdf_path),
            output_path=str(output_path)
        )
        
        # Sonuçları göster
        print("\n" + "="*70)
        print("📊 ÇIKARILAN VERİ ÖZETİ")
        print("="*70)
        
        print(f"\n🏛️  Belge Adı: {result.get('document_name', 'NULL')}")
        print(f"📄 Belge No: {result.get('document_number', 'NULL')}")
        print(f"📝 Belge Tipi: {result.get('document_type', 'NULL')}")
        print(f"📅 Yayın Tarihi: {result.get('publication_date', 'NULL')}")
        print(f"⚡ Yürürlük Tarihi: {result.get('effective_date', 'NULL')}")
        print(f"🏢 Yayınlayan Kurum: {result.get('issuing_authority', 'NULL')}")
        
        if result.get('sectors_covered') and result['sectors_covered'] != "NULL":
            print(f"\n🏭 Kapsanan Sektörler ({len(result['sectors_covered'])}):")
            for sector in result['sectors_covered'][:5]:  # İlk 5'i göster
                print(f"   • {sector}")
            if len(result['sectors_covered']) > 5:
                print(f"   ... ve {len(result['sectors_covered']) - 5} tane daha")
        
        if result.get('key_obligations') and result['key_obligations'] != "NULL":
            print(f"\n📋 Ana Yükümlülükler ({len(result['key_obligations'])}):")
            for i, obligation in enumerate(result['key_obligations'][:3], 1):
                print(f"   {i}. {obligation[:100]}...")
        
        print("\n" + "="*70)
        print(f"💾 Tam veri şuraya kaydedildi: {output_path}")
        print("="*70)
        
        logger.info("İşlem başarıyla tamamlandı!")
        
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}", exc_info=True)
        print(f"\n❌ Hata: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
