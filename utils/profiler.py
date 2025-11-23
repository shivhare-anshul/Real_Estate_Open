"""
Profiling utilities for performance monitoring
Simple time-based profiling without external dependencies
"""

import time
import functools
from typing import Callable, Any
from utils.logger import logger
from config.settings import settings

class PerformanceProfiler:
    """Performance profiler for functions and methods"""
    
    def __init__(self, enable_profiling: bool = True):
        """
        Initialize profiler
        
        Args:
            enable_profiling: Whether to enable profiling
        """
        self.enable_profiling = enable_profiling and settings.ENABLE_LOGGING
    
    def time_it(self, func: Callable) -> Callable:
        """
        Decorator to measure execution time
        
        Args:
            func: Function to profile
            
        Returns:
            Wrapped function with timing
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enable_profiling:
                return func(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"⏱️ {func.__name__} executed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {func.__name__} failed after {execution_time:.4f} seconds: {e}")
                raise
        
        return wrapper

# Global profiler instance
profiler = PerformanceProfiler()

# Convenience decorator
def time_function(func: Callable) -> Callable:
    """
    Decorator to time a function
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function with timing
    """
    return profiler.time_it(func)

__all__ = ["PerformanceProfiler", "time_function", "profiler"]
