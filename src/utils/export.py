"""
Export yardımcı fonksiyonları - CSV, Excel, SQL çıktı formatları
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def export_to_csv(data: Dict[str, Any], output_path: str, flatten: bool = True) -> None:
    """
    JSON verisini CSV formatında kaydeder.
    
    Args:
        data: JSON verisi
        output_path: CSV dosya yolu
        flatten: İç içe objeleri düzleştir
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Metadata ve liste alanlarını temizle
    clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
    
    # Liste alanlarını string'e çevir
    for key, value in clean_data.items():
        if isinstance(value, list):
            clean_data[key] = '; '.join(str(item) for item in value)
        elif isinstance(value, dict):
            clean_data[key] = json.dumps(value, ensure_ascii=False)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=clean_data.keys())
        writer.writeheader()
        writer.writerow(clean_data)


def export_batch_to_csv(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Birden fazla JSON verisini tek CSV'ye kaydeder.
    
    Args:
        results: JSON verisi listesi
        output_path: CSV dosya yolu
    """
    if not results:
        return
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Tüm alanları topla
    all_fields = set()
    clean_results = []
    
    for data in results:
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Liste alanlarını string'e çevir
        for key, value in clean_data.items():
            if isinstance(value, list):
                clean_data[key] = '; '.join(str(item) for item in value)
            elif isinstance(value, dict):
                clean_data[key] = json.dumps(value, ensure_ascii=False)
        
        clean_results.append(clean_data)
        all_fields.update(clean_data.keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
        writer.writeheader()
        writer.writerows(clean_results)


def export_to_excel(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    JSON verilerini Excel formatında kaydeder.
    
    Args:
        results: JSON verisi listesi
        output_path: Excel dosya yolu
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas yüklü değil. 'pip install pandas openpyxl' komutunu çalıştırın.")
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # DataFrame'e dönüştür
    clean_results = []
    for data in results:
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Liste alanlarını string'e çevir
        for key, value in clean_data.items():
            if isinstance(value, list):
                clean_data[key] = '; '.join(str(item) for item in value)
            elif isinstance(value, dict):
                clean_data[key] = json.dumps(value, ensure_ascii=False)
        
        clean_results.append(clean_data)
    
    df = pd.DataFrame(clean_results)
    
    # Excel'e kaydet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Documents')


def export_to_sql_inserts(results: List[Dict[str, Any]], table_name: str = "documents", output_path: Optional[str] = None) -> str:
    """
    JSON verilerini SQL INSERT statement'larına dönüştürür.
    
    Args:
        results: JSON verisi listesi
        table_name: Tablo adı
        output_path: SQL dosya yolu (None ise string döner)
        
    Returns:
        SQL INSERT statements
    """
    if not results:
        return ""
    
    sql_lines = []
    
    # Tablo şemasını oluştur
    sample = results[0]
    columns = [k for k in sample.keys() if not k.startswith('_')]
    
    sql_lines.append(f"-- Auto-generated SQL INSERT statements")
    sql_lines.append(f"-- Table: {table_name}")
    sql_lines.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for data in results:
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Liste alanlarını string'e çevir
        for key, value in clean_data.items():
            if isinstance(value, list):
                clean_data[key] = '; '.join(str(item) for item in value)
            elif isinstance(value, dict):
                clean_data[key] = json.dumps(value, ensure_ascii=False)
        
        # INSERT statement oluştur
        values = []
        for col in columns:
            val = clean_data.get(col, 'NULL')
            if val == 'NULL' or val is None:
                values.append('NULL')
            else:
                # String escape
                val_str = str(val).replace("'", "''")
                values.append(f"'{val_str}'")
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        sql_lines.append(sql)
    
    sql_content = '\n'.join(sql_lines)
    
    # Dosyaya kaydet
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
    
    return sql_content
