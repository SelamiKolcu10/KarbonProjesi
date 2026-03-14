"""
İstatistik ve raporlama yardımcı fonksiyonları
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path


class ProcessingStats:
    """PDF işleme istatistiklerini takip eden sınıf"""
    
    def __init__(self):
        self.total_processed = 0
        self.successful = 0
        self.failed = 0
        self.total_time = 0.0
        self.total_pages = 0
        self.total_characters = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.retry_count = 0
        self.chunk_operations = 0
        self.errors = []
        self.processing_history = []
    
    def record_success(self, metadata: Dict[str, Any]) -> None:
        """Başarılı işlem kaydı"""
        self.total_processed += 1
        self.successful += 1
        self.total_time += metadata.get('processing_time_seconds', 0)
        self.total_pages += metadata.get('page_count', 0)
        self.total_characters += metadata.get('text_length', 0)
        
        if metadata.get('used_chunking'):
            self.chunk_operations += 1
        
        self.processing_history.append({
            'timestamp': datetime.now().isoformat(),
            'file': metadata.get('source_file'),
            'status': 'success',
            'duration': metadata.get('processing_time_seconds')
        })
    
    def record_cache_hit(self) -> None:
        """Cache hit kaydı"""
        self.cache_hits += 1
        self.total_processed += 1
        self.successful += 1
    
    def record_cache_miss(self) -> None:
        """Cache miss kaydı"""
        self.cache_misses += 1
    
    def record_failure(self, filename: str, error: str) -> None:
        """Başarısız işlem kaydı"""
        self.total_processed += 1
        self.failed += 1
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'error': error
        })
        
        self.processing_history.append({
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'status': 'failed',
            'error': error
        })
    
    def record_retry(self) -> None:
        """Retry kaydı"""
        self.retry_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """İstatistik özeti döndürür"""
        return {
            'total_processed': self.total_processed,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': round(self.successful / self.total_processed * 100, 2) if self.total_processed > 0 else 0,
            'average_time_seconds': round(self.total_time / self.successful, 2) if self.successful > 0 else 0,
            'total_pages': self.total_pages,
            'average_pages': round(self.total_pages / self.successful, 2) if self.successful > 0 else 0,
            'total_characters': self.total_characters,
            'cache_hit_rate': round(self.cache_hits / (self.cache_hits + self.cache_misses) * 100, 2) if (self.cache_hits + self.cache_misses) > 0 else 0,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'retry_count': self.retry_count,
            'chunk_operations': self.chunk_operations,
            'error_count': len(self.errors)
        }
    
    def get_detailed_report(self) -> str:
        """Detaylı rapor metni döndürür"""
        summary = self.get_summary()
        
        report = []
        report.append("="*60)
        report.append("📊 DATA EXTRACTOR İSTATİSTİKLERİ")
        report.append("="*60)
        report.append("")
        report.append(f"Toplam İşlenen:     {summary['total_processed']} belge")
        report.append(f"Başarılı:           {summary['successful']} belge")
        report.append(f"Başarısız:          {summary['failed']} belge")
        report.append(f"Başarı Oranı:       {summary['success_rate']}%")
        report.append("")
        report.append(f"Ortalama Süre:      {summary['average_time_seconds']} saniye/belge")
        report.append(f"Toplam Sayfa:       {summary['total_pages']} sayfa")
        report.append(f"Ortalama Sayfa:     {summary['average_pages']} sayfa/belge")
        report.append(f"Toplam Karakter:    {summary['total_characters']:,} karakter")
        report.append("")
        report.append(f"Cache Hit Rate:     {summary['cache_hit_rate']}%")
        report.append(f"Cache Hits:         {summary['cache_hits']}")
        report.append(f"Cache Misses:       {summary['cache_misses']}")
        report.append("")
        report.append(f"Retry Sayısı:       {summary['retry_count']}")
        report.append(f"Chunk İşlemleri:    {summary['chunk_operations']}")
        report.append("")
        
        if self.errors:
            report.append(f"❌ HATALAR ({len(self.errors)}):")
            for i, error in enumerate(self.errors[-5:], 1):  # Son 5 hata
                report.append(f"  {i}. {error['file']}: {error['error'][:50]}...")
        
        report.append("="*60)
        
        return '\n'.join(report)
    
    def save_report(self, output_path: str) -> None:
        """Raporu dosyaya kaydeder"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'errors': self.errors,
            'processing_history': self.processing_history
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def reset(self) -> None:
        """İstatistikleri sıfırlar"""
        self.__init__()
