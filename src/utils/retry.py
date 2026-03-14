"""
Retry mekanizması - API hatalarında tekrar deneme
"""

import time
import logging
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Exponential backoff ile retry decorator.
    
    Args:
        max_retries: Maksimum deneme sayısı
        initial_delay: İlk bekleme süresi (saniye)
        backoff_factor: Her denemede bekleme süresinin çarpanı
        exceptions: Yakalanacak exception'lar
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            retries = 0
            delay = initial_delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"{func.__name__} başarısız oldu ({max_retries} deneme sonrası): {str(e)}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} başarısız, tekrar deneniyor... "
                        f"({retries}/{max_retries}) - Bekleniyor: {delay:.1f}s"
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimiter:
    """API rate limiting için basit sınıf"""
    
    def __init__(self, calls_per_minute: int = 10):
        """
        Args:
            calls_per_minute: Dakikada maksimum call sayısı
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time = 0.0
    
    def wait_if_needed(self) -> None:
        """Gerekirse rate limit için bekler"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            logger.debug(f"Rate limit: {sleep_time:.2f}s bekleniyor...")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
