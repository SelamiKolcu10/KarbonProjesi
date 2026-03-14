"""
Dil tespiti yardımcı fonksiyonları
"""

from typing import Tuple, Optional
import re


# Dil-spesifik kelime setleri
LANGUAGE_KEYWORDS = {
    'en': {
        'keywords': ['the', 'and', 'is', 'of', 'to', 'in', 'that', 'for', 'it', 'with', 
                     'this', 'shall', 'regulation', 'directive', 'article'],
        'common_patterns': [r'\bthe\b', r'\band\b', r'\bshall\b', r'\barticle\b']
    },
    'tr': {
        'keywords': ['ve', 'bu', 'bir', 'için', 'ile', 'olan', 'madde', 'yönetmelik'],
        'common_patterns': [r'\bve\b', r'\bbir\b', r'\bmadde\b']
    },
    'de': {
        'keywords': ['und', 'der', 'die', 'das', 'ist', 'zu', 'den', 'artikel'],
        'common_patterns': [r'\bund\b', r'\bder\b', r'\bartikel\b']
    },
    'fr': {
        'keywords': ['le', 'la', 'et', 'de', 'un', 'est', 'pour', 'article'],
        'common_patterns': [r'\blet\b', r'\bde\b', r'\barticle\b']
    },
    'es': {
        'keywords': ['el', 'la', 'y', 'de', 'un', 'es', 'para', 'artículo'],
        'common_patterns': [r'\bel\b', r'\by\b', r'\bartículo\b']
    }
}


def detect_language(text: str, sample_size: int = 5000) -> Tuple[str, float]:
    """
    Metnin dilini tespit eder (basit keyword bazlı).
    
    Args:
        text: Metin
        sample_size: Analiz edilecek karakter sayısı
        
    Returns:
        (dil_kodu, güven_skoru) tuple
    """
    # İlk N karakteri al
    sample = text[:sample_size].lower()
    
    scores = {}
    
    for lang, config in LANGUAGE_KEYWORDS.items():
        score = 0
        
        # Keyword kontrolü
        for keyword in config['keywords']:
            # Kelime sınırlarıyla arama
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, sample))
            score += matches
        
        scores[lang] = score
    
    # En yüksek skora sahip dil
    if not scores or max(scores.values()) == 0:
        return 'unknown', 0.0
    
    detected_lang = str(max(scores.items(), key=lambda x: x[1])[0])
    total_matches = sum(scores.values())
    confidence = scores[detected_lang] / total_matches if total_matches > 0 else 0.0
    
    return detected_lang, round(confidence, 2)


def detect_language_advanced(text: str) -> Tuple[str, float]:
    """
    Gelişmiş dil tespiti (langdetect kütüphanesi ile).
    
    Args:
        text: Metin
        
    Returns:
        (dil_kodu, güven_skoru) tuple
    """
    try:
        from langdetect import detect, detect_langs  # type: ignore
        
        # En olası dil
        lang = detect(text[:10000])
        
        # Güven skoru
        langs = detect_langs(text[:10000])
        confidence = next((l.prob for l in langs if l.lang == lang), 0.0)  # type: ignore
        
        return lang, round(confidence, 2)
        
    except ImportError:
        # Fallback: basit yöntem
        return detect_language(text)
    except Exception:
        return 'unknown', 0.0
