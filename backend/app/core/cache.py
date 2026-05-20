"""
Redis Caching Utility Module

Provides caching mechanisms for frequently accessed data using Redis,
including validation results, quality metrics, and dataset information.
"""

import redis
import json
import logging
from typing import Optional, Any, Dict, List, Callable
from functools import wraps
from datetime import timedelta
import pickle
import hashlib

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache manager for application-wide caching.
    
    Supports caching of validation results, metrics, and other frequently accessed data.
    """
    
    # Cache key prefixes
    PREFIX_VALIDATION = "validation:"
    PREFIX_METRICS = "metrics:"
    PREFIX_DATASET = "dataset:"
    PREFIX_ANOMALY = "anomaly:"
    PREFIX_RECONCILIATION = "reconciliation:"
    PREFIX_SESSION = "session:"
    
    # Default TTLs (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    VALIDATION_TTL = 1800  # 30 minutes
    METRICS_TTL = 3600  # 1 hour
    DATASET_TTL = 7200  # 2 hours
    ANOMALY_TTL = 1800  # 30 minutes
    SESSION_TTL = 86400  # 24 hours
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        socket_connect_timeout: int = 5
    ):
        """
        Initialize Redis cache connection.
        
        Args:
            host (str): Redis host address
            port (int): Redis port
            db (int): Redis database number
            password (Optional[str]): Redis password if required
            decode_responses (bool): Decode responses to strings
            socket_connect_timeout (int): Connection timeout in seconds
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=socket_connect_timeout
            )
            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info(f"Redis cache connected to {host}:{port}")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"Redis cache connection failed: {str(e)}. Caching will be disabled.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis cache is available."""
        return self.is_connected and self.redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached value or None
        """
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL
    ) -> bool:
        """
        Store value in cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int): Time to live in seconds
            
        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern (str): Key pattern (e.g., "validation:*")
            
        Returns:
            int: Number of keys deleted
        """
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern from cache: {str(e)}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if key exists
        """
        if not self.is_available():
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment numeric value in cache.
        
        Args:
            key (str): Cache key
            amount (int): Amount to increment by
            
        Returns:
            Optional[int]: New value or None
        """
        if not self.is_available():
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache value: {str(e)}")
            return None
    
    def flush_all(self) -> bool:
        """
        Clear all cache data.
        
        Args:
            flush_all (bool): Confirm flushing all data
            
        Returns:
            bool: Success status
        """
        if not self.is_available():
            return False
        
        try:
            self.redis_client.flushdb()
            logger.warning("Cache flushed")
            return True
        except Exception as e:
            logger.error(f"Error flushing cache: {str(e)}")
            return False
    
    # Convenience methods for specific cache types
    
    def cache_validation_result(
        self,
        dataset_id: int,
        validation_id: int,
        result: Dict
    ) -> bool:
        """Cache validation result."""
        key = f"{self.PREFIX_VALIDATION}ds:{dataset_id}:val:{validation_id}"
        return self.set(key, result, ttl=self.VALIDATION_TTL)
    
    def get_validation_result(
        self,
        dataset_id: int,
        validation_id: int
    ) -> Optional[Dict]:
        """Retrieve cached validation result."""
        key = f"{self.PREFIX_VALIDATION}ds:{dataset_id}:val:{validation_id}"
        return self.get(key)
    
    def invalidate_dataset_validations(self, dataset_id: int) -> int:
        """Invalidate all validations for a dataset."""
        pattern = f"{self.PREFIX_VALIDATION}ds:{dataset_id}:*"
        return self.delete_pattern(pattern)
    
    def cache_quality_score(
        self,
        dataset_id: int,
        score: Dict
    ) -> bool:
        """Cache quality score."""
        key = f"{self.PREFIX_METRICS}quality:ds:{dataset_id}"
        return self.set(key, score, ttl=self.METRICS_TTL)
    
    def get_quality_score(self, dataset_id: int) -> Optional[Dict]:
        """Retrieve cached quality score."""
        key = f"{self.PREFIX_METRICS}quality:ds:{dataset_id}"
        return self.get(key)
    
    def invalidate_quality_score(self, dataset_id: int) -> bool:
        """Invalidate cached quality score."""
        key = f"{self.PREFIX_METRICS}quality:ds:{dataset_id}"
        return self.delete(key)
    
    def cache_dataset(self, dataset_id: int, data: Dict) -> bool:
        """Cache dataset information."""
        key = f"{self.PREFIX_DATASET}id:{dataset_id}"
        return self.set(key, data, ttl=self.DATASET_TTL)
    
    def get_dataset(self, dataset_id: int) -> Optional[Dict]:
        """Retrieve cached dataset."""
        key = f"{self.PREFIX_DATASET}id:{dataset_id}"
        return self.get(key)
    
    def invalidate_dataset(self, dataset_id: int) -> bool:
        """Invalidate cached dataset."""
        key = f"{self.PREFIX_DATASET}id:{dataset_id}"
        return self.delete(key)
    
    def cache_anomaly_result(
        self,
        dataset_id: int,
        anomaly_id: int,
        result: Dict
    ) -> bool:
        """Cache anomaly detection result."""
        key = f"{self.PREFIX_ANOMALY}ds:{dataset_id}:anomaly:{anomaly_id}"
        return self.set(key, result, ttl=self.ANOMALY_TTL)
    
    def get_anomaly_result(
        self,
        dataset_id: int,
        anomaly_id: int
    ) -> Optional[Dict]:
        """Retrieve cached anomaly result."""
        key = f"{self.PREFIX_ANOMALY}ds:{dataset_id}:anomaly:{anomaly_id}"
        return self.get(key)
    
    def invalidate_dataset_anomalies(self, dataset_id: int) -> int:
        """Invalidate all anomalies for a dataset."""
        pattern = f"{self.PREFIX_ANOMALY}ds:{dataset_id}:*"
        return self.delete_pattern(pattern)


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cache_result(
    prefix: str,
    ttl: int = RedisCache.DEFAULT_TTL,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.
    
    Args:
        prefix (str): Cache key prefix
        ttl (int): Time to live in seconds
        key_builder (Optional[Callable]): Custom key builder function
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}:{v}" for k, v in kwargs.items())
                key_parts = [prefix, args_str, kwargs_str]
                cache_key = ":".join(p for p in key_parts if p)
            
            # Try to get from cache
            if cache.is_available():
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
                logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache by pattern.
    
    Args:
        pattern (str): Key pattern to invalidate
        
    Returns:
        int: Number of keys deleted
    """
    cache = get_cache()
    return cache.delete_pattern(pattern)


# Initialize module logger
logger = logging.getLogger(__name__)
