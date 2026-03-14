"""
Data Extractor v3.0 - Gelişmiş Özellikler Demo
Bu dosya yeni 6 özelliği gösterir:
1. Batch Processing
2. Confidence Score
3. Multi-Format Export
4. Document Summary
5. Language Detection
6. Statistics & Reporting
"""

import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Proje kökünü ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.data_extractor import DataExtractor

# Loglama setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction_v3.log'),
        logging.StreamHandler()
    ]
)

# .env yükle
load_dotenv()


def demo_single_document():
    """Tek belge işleme - yeni özelliklerle"""
    print("\n" + "="*60)
    print("DEMO 1: TEK BELGE İŞLEME (Yeni Özellikler)")
    print("="*60)
    
    # Extractor oluştur (statistics enabled)
    extractor = DataExtractor(
        llm_provider="gemini",
        use_cache=True,
        enable_stats=True
    )
    
    # PDF işle
    pdf_path = project_root / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf"
    result = extractor.process_document(
        pdf_path=str(pdf_path),
        output_path="output/demo_v3/single_document.json"
    )
    
    # 🆕 Confidence Score
    confidence = result["_metadata"]["confidence_score"]
    print(f"\n✨ Confidence Score: {confidence}")
    
    # 🆕 Language Detection
    detected_lang = result["_metadata"]["detected_language"]
    lang_conf = result["_metadata"]["language_confidence"]
    print(f"🌍 Detected Language: {detected_lang} (confidence: {lang_conf})")
    
    # 🆕 Document Summary
    summary = extractor.generate_summary(result)
    print(f"\n📝 Summary:\n{summary}\n")
    
    # 🆕 Export to CSV
    extractor.export_to_csv(result, "output/demo_v3/single_document.csv")
    print("📄 CSV export: output/demo_v3/single_document.csv")


def demo_batch_processing():
    """Batch processing demo"""
    print("\n" + "="*60)
    print("DEMO 2: BATCH PROCESSING")
    print("="*60)
    
    extractor = DataExtractor(
        llm_provider="gemini",
        use_cache=True,
        enable_stats=True
    )
    
    # Birden fazla PDF
    pdf_paths = [
        project_root / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf",
        project_root / "mevzuat_docs" / "CELEX_32023R1773_EN_TXT.pdf",
        project_root / "mevzuat_docs" / "Guidance document on CBAM implementation for importers of goods into the EU.pdf"
    ]
    
    # 🆕 Batch processing
    results = extractor.process_documents_batch(
        pdf_paths=[str(p) for p in pdf_paths if p.exists()],
        output_dir="output/demo_v3/batch",
        use_chunking=True,
        stop_on_error=False
    )
    
    print(f"\n✅ Processed {len(results)} documents")
    
    # 🆕 Export to Excel
    extractor.export_to_excel(results, "output/demo_v3/batch_results.xlsx")
    print("📊 Excel export: output/demo_v3/batch_results.xlsx")
    
    # 🆕 Export to CSV
    extractor.export_batch_to_csv(results, "output/demo_v3/batch_results.csv")
    print("📄 CSV export: output/demo_v3/batch_results.csv")
    
    # 🆕 Export to SQL
    extractor.export_to_sql(results, table_name="cbam_documents", output_path="output/demo_v3/batch_results.sql")
    print("🗄️  SQL export: output/demo_v3/batch_results.sql")


def demo_statistics():
    """İstatistik raporlama demo"""
    print("\n" + "="*60)
    print("DEMO 3: STATISTICS & REPORTING")
    print("="*60)
    
    extractor = DataExtractor(
        llm_provider="gemini",
        use_cache=True,
        enable_stats=True
    )
    
    # Birkaç belge işle (demo için)
    pdf_paths = [
        project_root / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf",
        project_root / "mevzuat_docs" / "CELEX_32023R1773_EN_TXT.pdf",
    ]
    
    for pdf_path in pdf_paths:
        if pdf_path.exists():
            try:
                extractor.process_document(str(pdf_path))
            except Exception as e:
                print(f"Error: {e}")
    
    # 🆕 İstatistik özeti
    stats = extractor.get_stats_summary()
    print("\n📊 STATISTICS SUMMARY:")
    print(f"   Total Processed: {stats['total_processed']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Success Rate: {stats['success_rate']}%")
    print(f"   Average Time: {stats['average_time_seconds']} seconds")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']}%")
    
    # 🆕 Detaylı rapor
    detailed_report = extractor.get_stats_report()
    print("\n" + detailed_report)
    
    # 🆕 Raporu kaydet
    extractor.save_stats_report("output/demo_v3/stats_report.json")
    print("\n💾 Stats report saved: output/demo_v3/stats_report.json")


def demo_all_features():
    """Tüm özellikleri tek seferde demo"""
    print("\n" + "="*60)
    print("DEMO 4: TÜM ÖZELLİKLER BİRARADA")
    print("="*60)
    
    extractor = DataExtractor(
        llm_provider="gemini",
        use_cache=True,
        cache_ttl_hours=24,
        max_retries=3,
        chunk_size=15000,
        rate_limit_per_minute=10,
        enable_stats=True
    )
    
    # PDF klasöründeki tüm dosyaları al
    mevzuat_dir = project_root / "mevzuat_docs"
    pdf_paths = list(mevzuat_dir.glob("*.pdf"))[:3]  # İlk 3'ünü al
    
    print(f"\n📁 Found {len(pdf_paths)} PDFs to process\n")
    
    # Batch processing
    results = extractor.process_documents_batch(
        pdf_paths=[str(p) for p in pdf_paths],
        output_dir="output/demo_v3/all_features",
        use_chunking=True,
        stop_on_error=False
    )
    
    # Her belge için özet
    print("\n" + "="*60)
    print("DOCUMENT SUMMARIES:")
    print("="*60)
    for i, result in enumerate(results, 1):
        if "error" not in result:
            summary = extractor.generate_summary(result)
            print(f"\n[{i}] {result.get('document_name', 'Unknown')}")
            print(f"    Language: {result['_metadata']['detected_language']}")
            print(f"    Confidence: {result['_metadata']['confidence_score']}")
            print(f"    Summary: {summary[:100]}...")
    
    # Export tüm formatlara
    print("\n" + "="*60)
    print("EXPORTING TO MULTIPLE FORMATS:")
    print("="*60)
    
    extractor.export_batch_to_csv(results, "output/demo_v3/all_results.csv")
    print("✅ CSV: output/demo_v3/all_results.csv")
    
    try:
        extractor.export_to_excel(results, "output/demo_v3/all_results.xlsx")
        print("✅ Excel: output/demo_v3/all_results.xlsx")
    except ImportError:
        print("⚠️  Excel export skipped (pandas not installed)")
    
    extractor.export_to_sql(results, "cbam_docs", "output/demo_v3/all_results.sql")
    print("✅ SQL: output/demo_v3/all_results.sql")
    
    # İstatistikler
    print("\n" + extractor.get_stats_report())
    extractor.save_stats_report("output/demo_v3/final_stats.json")
    print("\n✅ Stats report: output/demo_v3/final_stats.json")


if __name__ == "__main__":
    # Tüm demoları çalıştır
    try:
        demo_single_document()
        demo_batch_processing()
        demo_statistics()
        demo_all_features()
        
        print("\n" + "="*60)
        print("✅ TÜM DEMOLAR TAMAMLANDI!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
