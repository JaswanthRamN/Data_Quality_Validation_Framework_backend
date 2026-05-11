import pandas as pd
from typing import Dict, Any

def compare_row_counts(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    source_name: str = "Source",
    target_name: str = "Target"
) -> Dict[str, Any]:
    """
    Compare row counts between two DataFrames.
    
    Args:
        source_df: Source DataFrame
        target_df: Target DataFrame
        source_name: Name of source dataset
        target_name: Name of target dataset
    
    Returns:
        Dictionary with comparison results
    """
    try:
        source_count = len(source_df)
        target_count = len(target_df)
        difference = source_count - target_count
        percentage_diff = round((difference / source_count * 100), 2) if source_count > 0 else 0
        
        match = source_count == target_count
        
        return {
            "reconciliation_type": "row_count",
            "match": match,
            "source": {
                "name": source_name,
                "row_count": source_count
            },
            "target": {
                "name": target_name,
                "row_count": target_count
            },
            "difference": difference,
            "percentage_difference": percentage_diff,
            "status": "MATCHED" if match else "MISMATCHED"
        }
    
    except Exception as e:
        return {
            "reconciliation_type": "row_count",
            "error": str(e),
            "status": "ERROR"
        }

def compare_row_counts_with_filter(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    filter_column: str = None,
    filter_value: Any = None,
    source_name: str = "Source",
    target_name: str = "Target"
) -> Dict[str, Any]:
    """
    Compare row counts with optional filtering.
    
    Args:
        source_df: Source DataFrame
        target_df: Target DataFrame
        filter_column: Column to filter on
        filter_value: Value to filter by
        source_name: Name of source dataset
        target_name: Name of target dataset
    
    Returns:
        Dictionary with filtered comparison results
    """
    try:
        source_filtered = source_df
        target_filtered = target_df
        
        if filter_column and filter_value is not None:
            if filter_column in source_df.columns:
                source_filtered = source_df[source_df[filter_column] == filter_value]
            if filter_column in target_df.columns:
                target_filtered = target_df[target_df[filter_column] == filter_value]
        
        source_count = len(source_filtered)
        target_count = len(target_filtered)
        difference = source_count - target_count
        percentage_diff = round((difference / source_count * 100), 2) if source_count > 0 else 0
        
        match = source_count == target_count
        
        return {
            "reconciliation_type": "row_count_filtered",
            "match": match,
            "filter": {
                "column": filter_column,
                "value": filter_value
            },
            "source": {
                "name": source_name,
                "row_count": source_count
            },
            "target": {
                "name": target_name,
                "row_count": target_count
            },
            "difference": difference,
            "percentage_difference": percentage_diff,
            "status": "MATCHED" if match else "MISMATCHED"
        }
    
    except Exception as e:
        return {
            "reconciliation_type": "row_count_filtered",
            "error": str(e),
            "status": "ERROR"
        }

def get_missing_rows(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    key_column: str
) -> Dict[str, Any]:
    """
    Find rows in source that are missing in target.
    
    Args:
        source_df: Source DataFrame
        target_df: Target DataFrame
        key_column: Column to use as key for comparison
    
    Returns:
        Dictionary with missing rows information
    """
    try:
        if key_column not in source_df.columns or key_column not in target_df.columns:
            return {
                "error": f"Key column '{key_column}' not found in one or both DataFrames",
                "status": "ERROR"
            }
        
        source_keys = set(source_df[key_column])
        target_keys = set(target_df[key_column])
        
        missing_in_target = source_keys - target_keys
        extra_in_target = target_keys - source_keys
        
        missing_df = source_df[source_df[key_column].isin(missing_in_target)]
        extra_df = target_df[target_df[key_column].isin(extra_in_target)]
        
        return {
            "reconciliation_type": "missing_rows",
            "key_column": key_column,
            "missing_in_target": {
                "count": len(missing_in_target),
                "keys": list(missing_in_target)[:100]  # Limit to 100 for response size
            },
            "extra_in_target": {
                "count": len(extra_in_target),
                "keys": list(extra_in_target)[:100]
            },
            "match": len(missing_in_target) == 0 and len(extra_in_target) == 0,
            "status": "MATCHED" if len(missing_in_target) == 0 and len(extra_in_target) == 0 else "MISMATCHED"
        }
    
    except Exception as e:
        return {
            "reconciliation_type": "missing_rows",
            "error": str(e),
            "status": "ERROR"
        }
