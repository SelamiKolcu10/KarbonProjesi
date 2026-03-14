"""
Data Extractor testleri
"""

try:
    import pytest  # type: ignore
except ImportError:
    pytest = None  # type: ignore

import json
from pathlib import Path
from src.agents.data_extractor import DataExtractor


class TestDataExtractor:
    """Data Extractor test sınıfı"""
    
    def test_initialization_gemini(self):
        """Gemini ile initialization testi"""
        # Mock API key ile
        extractor = DataExtractor(llm_provider="gemini", api_key="test_key")
        assert extractor.llm_provider == "gemini"
    
    def test_initialization_gpt(self):
        """GPT ile initialization testi"""
        extractor = DataExtractor(llm_provider="gpt", api_key="test_key")
        assert extractor.llm_provider == "gpt"
    
    def test_initialization_invalid_provider(self):
        """Geçersiz provider testi"""
        if pytest is None:
            return  # pytest yüklü değilse atla
        with pytest.raises(ValueError):  # type: ignore
            DataExtractor(llm_provider="invalid_provider", api_key="test_key")
    
    def test_clean_text(self):
        """Metin temizleme testi"""
        extractor = DataExtractor(llm_provider="gemini", api_key="test_key")
        
        dirty_text = "  Multiple   spaces   \n\n\n  and newlines  "
        clean = extractor.clean_text(dirty_text)
        
        assert "  " not in clean
        assert clean.strip() == clean
    
    def test_schema_validation(self):
        """Şema validasyon testi"""
        extractor = DataExtractor(llm_provider="gemini", api_key="test_key")
        
        # Eksik alanlar (güncel schema'ya göre)
        incomplete_data = {
            "document_metadata": "NULL",
            "reporting_period": "NULL"
        }
        
        # Validate method eksik alanları NULL ile doldurmalı
        extractor._validate_schema(incomplete_data)
        
        # Tüm alanlar mevcut olmalı (güncel schema alanları)
        assert "production" in incomplete_data
        assert incomplete_data["production"] == "NULL"
    
    def test_expected_schema_structure(self):
        """Beklenen şema yapısı testi"""
        schema = DataExtractor.EXPECTED_SCHEMA
        
        # Zorunlu alanlar (güncel schema'ya göre)
        required_fields = [
            "document_metadata",
            "reporting_period",
            "production",
            "energy_scope_1",
            "energy_scope_2",
            "validation_flags"
        ]
        
        for field in required_fields:
            assert field in schema


if __name__ == "__main__":
    if pytest is not None:
        pytest.main([__file__, "-v"])  # type: ignore
    else:
        print("pytest yüklü değil. 'pip install pytest' komutunu çalıştırın.")
