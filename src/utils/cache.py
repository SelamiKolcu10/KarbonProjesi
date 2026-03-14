"""
Cache yardımcı fonksiyonları
PDF işleme sonuçlarını cache'ler
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class PDFCache:
    """PDF işleme sonuçlarını cache'leyen sınıf"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Args:
            cache_dir: Cache dosyalarının saklanacağı dizin
            ttl_hours: Cache'in geçerli olacağı saat sayısı
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        Dosyanın SHA256 hash'ini hesaplar.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Hash string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Dosyayı parça parça oku (büyük dosyalar için)
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _get_cache_path(self, file_hash: str) -> Path:
        """Cache dosya yolunu döndürür"""
        return self.cache_dir / f"{file_hash}.json"
    
    def get(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Cache'den veri alır.
        
        Args:
            pdf_path: PDF dosyasının yolu
            
        Returns:
            Cache'lenmiş veri veya None
        """
        try:
            file_hash = self._get_file_hash(pdf_path)
            cache_path = self._get_cache_path(file_hash)
            
            if not cache_path.exists():
                return None
            
            # Cache dosyasını oku
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # TTL kontrolü
            cached_time = datetime.fromisoformat(cache_data.get("_cache_timestamp", "2000-01-01"))
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                # Cache eski, sil
                cache_path.unlink()
                return None
            
            return cache_data.get("data")
            
        except Exception:
            return None
    
    def set(self, pdf_path: str, data: Dict[str, Any]) -> None:
        """
        Veriyi cache'e kaydeder.
        
        Args:
            pdf_path: PDF dosyasının yolu
            data: Cache'lenecek veri
        """
        try:
            file_hash = self._get_file_hash(pdf_path)
            cache_path = self._get_cache_path(file_hash)
            
            cache_data = {
                "_cache_timestamp": datetime.now().isoformat(),
                "_pdf_path": str(pdf_path),
                "data": data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass  # Cache hatası önemli değil, sadece atlıyoruz
    
    def clear(self) -> int:
        """
        Tüm cache'i temizler.
        
        Returns:
            Silinen dosya sayısı
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
    
    def clear_expired(self) -> int:
        """
        Süresi dolmuş cache'leri temizler.
        
        Returns:
            Silinen dosya sayısı
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data.get("_cache_timestamp", "2000-01-01"))
                if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                    cache_file.unlink()
                    count += 1
            except Exception:
                # Bozuk cache dosyasını sil
                cache_file.unlink()
                count += 1
        
        return count
