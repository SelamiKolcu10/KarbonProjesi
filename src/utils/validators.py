"""
Veri validasyon yardımcı fonksiyonları
"""

import re
from datetime import datetime
from typing import Any, Optional


def is_valid_date(date_string: str, format: str = "%Y-%m-%d") -> bool:
    """
    Tarih string'inin geçerli olup olmadığını kontrol eder.
    
    Args:
        date_string: Tarih string'i
        format: Beklenen tarih formatı
        
    Returns:
        True eğer geçerli tarihse
    """
    if date_string == "NULL" or not date_string:
        return True
    
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def is_null_value(value: Any) -> bool:
    """
    Bir değerin NULL (eksik veri) olup olmadığını kontrol eder.
    
    Args:
        value: Kontrol edilecek değer
        
    Returns:
        True eğer NULL ise
    """
    if value is None:
        return True
    if isinstance(value, str) and value.strip().upper() in ["NULL", "N/A", "NONE", ""]:
        return True
    return False


def clean_document_number(doc_number: str) -> Optional[str]:
    """
    Belge numarasını temizler ve normalleştirir.
    
    Args:
        doc_number: Ham belge numarası
        
    Returns:
        Temizlenmiş belge numarası veya NULL
    """
    if is_null_value(doc_number):
        return "NULL"
    
    # Fazla boşlukları temizle
    cleaned = re.sub(r'\s+', ' ', doc_number.strip())
    
    return cleaned if cleaned else "NULL"


def validate_json_schema(data: dict, required_fields: list) -> tuple[bool, list]:
    """
    JSON verisinin gerekli alanları içerip içermediğini kontrol eder.
    
    Args:
        data: Kontrol edilecek dictionary
        required_fields: Gerekli alan isimleri
        
    Returns:
        (geçerli_mi, eksik_alanlar)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields
