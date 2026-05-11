import pandas as pd
from typing import Dict, List, Any, Optional

def compare_aggregations(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    agg_column: str,
    agg_function: str = "sum",
    group_by: Optional[str] = None,
    source_name: str = "Source",
    target_name: str = "Target"
) -> Dict[str, Any]:
    """
    Compare aggregated values between two DataFrames.
    
    Args:
        source_df: Source DataFrame
        target_df: Target DataFrame
        agg_column: Column to aggregate
        agg_function: Aggregation function (sum, count, avg, min, max)
        group_by: Optional column to group by
        source_name: Name of source dataset
        target_name: Name of target dataset
    
    Returns:
        Dictionary with aggregation comparison results
    """
    try:
        if agg_column not in source_df.columns or agg_column not in target_df.columns:
            return {
                "error": f"Column '{agg_column}' not found in one or both DataFrames",
                "status": "ERROR"
            }
        
        agg_func_map = {
            "sum": "sum",
            "count": "count",
            "avg": "mean",
            "average": "mean",
            "min": "min",
            "max": "max",
            "std": "std"
        }
        
        func = agg_func_map.get(agg_function.lower(), "sum")
        
        if group_by:
            # Grouped aggregation
            source_agg = source_df.groupby(group_by)[agg_column].agg(func)
            target_agg = target_df.groupby(group_by)[agg_column].agg(func)
            
            comparison = []
            all_groups = set(source_agg.index) | set(target_agg.index)
            
            for group in sorted(all_groups):
                source_val = source_agg.get(group, 0)
                target_val = target_agg.get(group, 0)
                difference = source_val - target_val if isinstance(source_val, (int, float)) else None
                
                comparison.append({
                    "group": group,
                    "source_value": source_val,
                    "target_value": target_val,
                    "difference": difference,
                    "match": source_val == target_val
                })
            
            matches = sum(1 for c in comparison if c["match"])
            
            return {
                "reconciliation_type": "aggregation_grouped",
                "agg_function": agg_function,
                "agg_column": agg_column,
                "group_by": group_by,
                "total_groups": len(all_groups),
                "matched_groups": matches,
                "mismatched_groups": len(all_groups) - matches,
                "comparison": comparison,
                "status": "MATCHED" if matches == len(all_groups) else "MISMATCHED"
            }
        
        else:
            # Overall aggregation
            source_val = source_df[agg_column].agg(func)
            target_val = target_df[agg_column].agg(func)
            difference = source_val - target_val if isinstance(source_val, (int, float)) else None
            
            percentage_diff = round((difference / source_val * 100), 2) if source_val != 0 else 0
            match = source_val == target_val
            
            return {
                "reconciliation_type": "aggregation",
                "agg_function": agg_function,
                "agg_column": agg_column,
                "source": {
                    "name": source_name,
                    "value": source_val
                },
                "target": {
                    "name": target_name,
                    "value": target_val
                },
                "difference": difference,
                "percentage_difference": percentage_diff,
                "match": match,
                "status": "MATCHED" if match else "MISMATCHED"
            }
    
    except Exception as e:
        return {
            "reconciliation_type": "aggregation",
            "error": str(e),
            "status": "ERROR"
        }

def compare_multiple_aggregations(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    aggregations: List[Dict[str, Any]],
    source_name: str = "Source",
    target_name: str = "Target"
) -> Dict[str, Any]:
    """
    Compare multiple aggregations at once.
    
    Args:
        source_df: Source DataFrame
        target_df: Target DataFrame
        aggregations: List of aggregation configs
                     Example: [
                         {"column": "amount", "function": "sum"},
                         {"column": "id", "function": "count"},
                         {"column": "price", "function": "avg"}
                     ]
        source_name: Name of source dataset
        target_name: Name of target dataset
    
    Returns:
        Dictionary with all aggregation comparisons
    """
    results = {
        "reconciliation_type": "multiple_aggregations",
        "source_name": source_name,
        "target_name": target_name,
        "aggregations": [],
        "total_checks": len(aggregations),
        "matched": 0,
        "mismatched": 0
    }
    
    for agg in aggregations:
        column = agg.get("column")
        func = agg.get("function", "sum")
        group_by = agg.get("group_by")
        
        result = compare_aggregations(
            source_df,
            target_df,
            column,
            func,
            group_by,
            source_name,
            target_name
        )
        
        if result.get("status") == "MATCHED":
            results["matched"] += 1
        elif result.get("status") == "MISMATCHED":
            results["mismatched"] += 1
        
        results["aggregations"].append(result)
    
    results["overall_status"] = "MATCHED" if results["mismatched"] == 0 else "MISMATCHED"
    
    return results

def get_column_statistics(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a numeric column.
    
    Args:
        df: DataFrame
        column: Column to analyze
    
    Returns:
        Dictionary with column statistics
    """
    try:
        if column not in df.columns:
            return {
                "error": f"Column '{column}' not found",
                "status": "ERROR"
            }
        
        col_data = df[column]
        
        stats = {
            "column": column,
            "count": col_data.count(),
            "null_count": col_data.isnull().sum(),
            "min": col_data.min() if pd.api.types.is_numeric_dtype(col_data) else None,
            "max": col_data.max() if pd.api.types.is_numeric_dtype(col_data) else None,
            "mean": col_data.mean() if pd.api.types.is_numeric_dtype(col_data) else None,
            "median": col_data.median() if pd.api.types.is_numeric_dtype(col_data) else None,
            "std": col_data.std() if pd.api.types.is_numeric_dtype(col_data) else None,
            "sum": col_data.sum() if pd.api.types.is_numeric_dtype(col_data) else None,
            "unique_count": col_data.nunique(),
            "dtype": str(col_data.dtype)
        }
        
        return stats
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "ERROR"
        }
