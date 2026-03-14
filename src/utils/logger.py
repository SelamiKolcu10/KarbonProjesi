"""
Loglama yardımcı fonksiyonları
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_dir: str = "logs", level=logging.INFO):
    """
    Logger oluşturur.
    
    Args:
        name: Logger adı
        log_dir: Log dosyalarının kaydedileceği dizin
        level: Log seviyesi
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Log dizinini oluştur
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # File handler
    log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Handlers ekle
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
