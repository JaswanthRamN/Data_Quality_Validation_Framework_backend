"""
Redis Cache Initialization

Initializes Redis cache for the application with configuration settings.
"""

import logging
from typing import Optional

from app.config import Settings
from app.core.cache import RedisCache, _cache_instance
from app.core.validation_cache import ValidationResultCache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages cache initialization and lifecycle for the application.
    """
    
    _instance: Optional['CacheManager'] = None
    _cache: Optional[RedisCache] = None
    _validation_cache: Optional[ValidationResultCache] = None
    
    @classmethod
    def initialize(cls, settings: Settings) -> 'CacheManager':
        """
        Initialize cache manager with settings.
        
        Args:
            settings (Settings): Application settings
            
        Returns:
            CacheManager: Cache manager instance
        """
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> Optional['CacheManager']:
        """Get cache manager instance."""
        return cls._instance
    
    def __init__(self, settings: Settings):
        """
        Initialize cache with settings.
        
        Args:
            settings (Settings): Application settings
        """
        self.settings = settings
        self._cache = None
        self._validation_cache = None
        
        if settings.ENABLE_CACHING:
            self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis cache with settings."""
        try:
            logger.info("Initializing Redis cache...")
            
            self._cache = RedisCache(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                password=self.settings.REDIS_PASSWORD,
                socket_connect_timeout=self.settings.REDIS_SOCKET_TIMEOUT
            )
            
            if self._cache.is_available():
                logger.info("Redis cache initialized successfully")
                
                # Update cache TTLs from settings
                RedisCache.VALIDATION_TTL = self.settings.REDIS_VALIDATION_TTL
                RedisCache.METRICS_TTL = self.settings.REDIS_METRICS_TTL
                RedisCache.DATASET_TTL = self.settings.REDIS_DATASET_TTL
                RedisCache.ANOMALY_TTL = self.settings.REDIS_ANOMALY_TTL
                RedisCache.SESSION_TTL = self.settings.REDIS_SESSION_TTL
                
                # Initialize validation cache
                self._validation_cache = ValidationResultCache(cache=self._cache)
                
                logger.info("Validation result cache initialized")
            else:
                logger.warning("Redis cache is not available, caching will be disabled")
                self._cache = None
        
        except Exception as e:
            logger.error(f"Error initializing Redis cache: {str(e)}")
            self._cache = None
    
    def get_cache(self) -> Optional[RedisCache]:
        """Get Redis cache instance."""
        return self._cache
    
    def get_validation_cache(self) -> Optional[ValidationResultCache]:
        """Get validation result cache instance."""
        return self._validation_cache
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled and available."""
        return self.settings.ENABLE_CACHING and self._cache is not None and self._cache.is_available()
    
    def shutdown(self):
        """Shutdown cache connections."""
        try:
            if self._cache and self._cache.redis_client:
                self._cache.redis_client.close()
                logger.info("Redis cache connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis cache: {str(e)}")


def init_cache(settings: Settings) -> CacheManager:
    """
    Initialize cache for application startup.
    
    Args:
        settings (Settings): Application settings
        
    Returns:
        CacheManager: Initialized cache manager
    """
    return CacheManager.initialize(settings)


def get_cache_manager() -> Optional[CacheManager]:
    """Get current cache manager instance."""
    return CacheManager.get_instance()
