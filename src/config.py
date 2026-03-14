"""
Konfigürasyon ayarları
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """Uygulama konfigürasyonu"""
    
    # Proje dizinleri
    BASE_DIR = Path(__file__).parent.parent
    MEVZUAT_DOCS_DIR = BASE_DIR / "mevzuat_docs"
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    
    # API anahtarları
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LLM ayarları
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")  # "gemini" veya "gpt"
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    
    # Data Extractor ayarları
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "15000"))  # LLM'e gönderilecek max karakter
    
    @classmethod
    def validate(cls):
        """Konfigürasyonu doğrular"""
        errors = []
        
        if cls.DEFAULT_LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY tanımlanmamış")
        
        if cls.DEFAULT_LLM_PROVIDER == "gpt" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY tanımlanmamış")
        
        if errors:
            raise ValueError(f"Konfigürasyon hatası: {', '.join(errors)}")
        
        # Dizinleri oluştur
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_api_key(cls, provider: str):
        """Belirtilen provider için API anahtarını döndürür"""
        if provider.lower() == "gemini":
            return cls.GEMINI_API_KEY
        elif provider.lower() == "gpt":
            return cls.OPENAI_API_KEY
        else:
            raise ValueError(f"Bilinmeyen provider: {provider}")
