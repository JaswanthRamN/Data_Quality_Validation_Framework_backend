"""
Validation Result Caching Module

Integrates Redis caching with validation results for improved performance.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.cache import get_cache, RedisCache
from app.crud import validation_crud
from app.models.validation_result import ValidationResult

logger = logging.getLogger(__name__)


class ValidationResultCache:
    """
    Manages caching of validation results with Redis.
    
    Provides methods to cache, retrieve, and invalidate validation results
    with automatic TTL management.
    """
    
    def __init__(self, cache: Optional[RedisCache] = None):
        """
        Initialize validation result cache.
        
        Args:
            cache (Optional[RedisCache]): Redis cache instance
        """
        self.cache = cache or get_cache()
    
    def cache_validation_results(
        self,
        dataset_id: int,
        results: List[ValidationResult],
        ttl: int = RedisCache.VALIDATION_TTL
    ) -> bool:
        """
        Cache validation results for a dataset.
        
        Args:
            dataset_id (int): Dataset ID
            results (List[ValidationResult]): Validation results to cache
            ttl (int): Time to live in seconds
            
        Returns:
            bool: Success status
        """
        if not results:
            return False
        
        try:
            # Convert results to serializable format
            serialized_results = [
                {
                    "id": r.id,
                    "dataset_id": r.dataset_id,
                    "column_name": r.column_name,
                    "rule_name": r.rule_name,
                    "value": r.value,
                    "is_valid": r.is_valid,
                    "error_message": r.error_message,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in results
            ]
            
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:results"
            success = self.cache.set(key, serialized_results, ttl=ttl)
            
            if success:
                logger.info(f"Cached {len(results)} validation results for dataset {dataset_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error caching validation results: {str(e)}")
            return False
    
    def get_cached_validation_results(
        self,
        dataset_id: int
    ) -> Optional[List[Dict]]:
        """
        Retrieve cached validation results for a dataset.
        
        Args:
            dataset_id (int): Dataset ID
            
        Returns:
            Optional[List[Dict]]: Cached results or None
        """
        try:
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:results"
            results = self.cache.get(key)
            
            if results:
                logger.debug(f"Retrieved cached validation results for dataset {dataset_id}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving cached validation results: {str(e)}")
            return None
    
    def cache_validation_summary(
        self,
        dataset_id: int,
        summary: Dict,
        ttl: int = RedisCache.VALIDATION_TTL
    ) -> bool:
        """
        Cache validation summary statistics.
        
        Args:
            dataset_id (int): Dataset ID
            summary (Dict): Summary statistics
            ttl (int): Time to live in seconds
            
        Returns:
            bool: Success status
        """
        try:
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:summary"
            success = self.cache.set(key, summary, ttl=ttl)
            
            if success:
                logger.info(f"Cached validation summary for dataset {dataset_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error caching validation summary: {str(e)}")
            return False
    
    def get_cached_validation_summary(
        self,
        dataset_id: int
    ) -> Optional[Dict]:
        """
        Retrieve cached validation summary.
        
        Args:
            dataset_id (int): Dataset ID
            
        Returns:
            Optional[Dict]: Cached summary or None
        """
        try:
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:summary"
            summary = self.cache.get(key)
            
            if summary:
                logger.debug(f"Retrieved cached validation summary for dataset {dataset_id}")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error retrieving cached validation summary: {str(e)}")
            return None
    
    def cache_column_results(
        self,
        dataset_id: int,
        column_name: str,
        results: List[ValidationResult],
        ttl: int = RedisCache.VALIDATION_TTL
    ) -> bool:
        """
        Cache validation results for a specific column.
        
        Args:
            dataset_id (int): Dataset ID
            column_name (str): Column name
            results (List[ValidationResult]): Validation results
            ttl (int): Time to live in seconds
            
        Returns:
            bool: Success status
        """
        if not results:
            return False
        
        try:
            serialized_results = [
                {
                    "id": r.id,
                    "rule_name": r.rule_name,
                    "value": r.value,
                    "is_valid": r.is_valid,
                    "error_message": r.error_message
                }
                for r in results
            ]
            
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:column:{column_name}"
            success = self.cache.set(key, serialized_results, ttl=ttl)
            
            if success:
                logger.info(f"Cached {len(results)} results for column {column_name} in dataset {dataset_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error caching column validation results: {str(e)}")
            return False
    
    def get_cached_column_results(
        self,
        dataset_id: int,
        column_name: str
    ) -> Optional[List[Dict]]:
        """
        Retrieve cached validation results for a column.
        
        Args:
            dataset_id (int): Dataset ID
            column_name (str): Column name
            
        Returns:
            Optional[List[Dict]]: Cached results or None
        """
        try:
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:column:{column_name}"
            results = self.cache.get(key)
            
            if results:
                logger.debug(f"Retrieved cached results for column {column_name}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving cached column results: {str(e)}")
            return None
    
    def invalidate_dataset_cache(self, dataset_id: int) -> int:
        """
        Invalidate all cache entries for a dataset.
        
        Args:
            dataset_id (int): Dataset ID
            
        Returns:
            int: Number of cache entries deleted
        """
        try:
            pattern = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:*"
            count = self.cache.delete_pattern(pattern)
            
            logger.info(f"Invalidated {count} cache entries for dataset {dataset_id}")
            
            return count
        
        except Exception as e:
            logger.error(f"Error invalidating dataset cache: {str(e)}")
            return 0
    
    def invalidate_column_cache(self, dataset_id: int, column_name: str) -> bool:
        """
        Invalidate cache for specific column.
        
        Args:
            dataset_id (int): Dataset ID
            column_name (str): Column name
            
        Returns:
            bool: Success status
        """
        try:
            key = f"{RedisCache.PREFIX_VALIDATION}dataset:{dataset_id}:column:{column_name}"
            success = self.cache.delete(key)
            
            if success:
                logger.info(f"Invalidated cache for column {column_name} in dataset {dataset_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error invalidating column cache: {str(e)}")
            return False
    
    def get_or_compute_validation_results(
        self,
        db: Session,
        dataset_id: int,
        force_refresh: bool = False
    ) -> Optional[List[Dict]]:
        """
        Get validation results from cache or compute if not cached.
        
        Args:
            db (Session): Database session
            dataset_id (int): Dataset ID
            force_refresh (bool): Force refresh from database
            
        Returns:
            Optional[List[Dict]]: Validation results
        """
        try:
            # Try cache first
            if not force_refresh:
                cached = self.get_cached_validation_results(dataset_id)
                if cached is not None:
                    logger.debug(f"Returning cached validation results for dataset {dataset_id}")
                    return cached
            
            # Fetch from database
            logger.debug(f"Fetching validation results from database for dataset {dataset_id}")
            results = validation_crud.get_validation_results_by_dataset(db, dataset_id)
            
            if results:
                # Cache the results
                self.cache_validation_results(dataset_id, results)
                
                # Convert to serializable format
                serialized = [
                    {
                        "id": r.id,
                        "dataset_id": r.dataset_id,
                        "column_name": r.column_name,
                        "rule_name": r.rule_name,
                        "value": r.value,
                        "is_valid": r.is_valid,
                        "error_message": r.error_message,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in results
                ]
                
                return serialized
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting validation results: {str(e)}")
            return None


# Global validation result cache instance
_validation_cache_instance: Optional[ValidationResultCache] = None


def get_validation_cache() -> ValidationResultCache:
    """Get or create global validation result cache instance."""
    global _validation_cache_instance
    if _validation_cache_instance is None:
        _validation_cache_instance = ValidationResultCache()
    return _validation_cache_instance
