import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class ValidationRule:
    def __init__(self, rule_name: str, column: str):
        self.rule_name = rule_name
        self.column = column
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "column": self.column,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round((self.passed / (self.passed + self.failed) * 100), 2) if (self.passed + self.failed) > 0 else 0,
            "errors": self.errors
        }

def check_null_values(df: pd.DataFrame, column: str, allow_null: bool = False) -> ValidationRule:
    """
    Check for null/missing values in a column.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        allow_null: Whether null values are allowed
    
    Returns:
        ValidationRule object with results
    """
    rule = ValidationRule("null_check", column)
    
    try:
        if column not in df.columns:
            rule.errors.append(f"Column '{column}' not found in DataFrame")
            rule.failed = len(df)
            return rule
        
        null_count = df[column].isnull().sum()
        total_rows = len(df)
        non_null_count = total_rows - null_count
        
        if allow_null:
            rule.passed = total_rows
            rule.failed = 0
        else:
            rule.passed = non_null_count
            rule.failed = null_count
            if null_count > 0:
                rule.errors.append(f"Found {null_count} null values in column '{column}'")
        
        return rule
    
    except Exception as e:
        rule.errors.append(f"Error during null check: {str(e)}")
        rule.failed = len(df)
        return rule

def check_duplicates(df: pd.DataFrame, column: str, allow_duplicates: bool = False) -> ValidationRule:
    """
    Check for duplicate values in a column.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        allow_duplicates: Whether duplicates are allowed
    
    Returns:
        ValidationRule object with results
    """
    rule = ValidationRule("duplicate_check", column)
    
    try:
        if column not in df.columns:
            rule.errors.append(f"Column '{column}' not found in DataFrame")
            rule.failed = len(df)
            return rule
        
        duplicate_count = df[column].duplicated().sum()
        total_rows = len(df)
        unique_rows = total_rows - duplicate_count
        
        if allow_duplicates:
            rule.passed = total_rows
            rule.failed = 0
        else:
            rule.passed = unique_rows
            rule.failed = duplicate_count
            if duplicate_count > 0:
                rule.errors.append(f"Found {duplicate_count} duplicate values in column '{column}'")
        
        return rule
    
    except Exception as e:
        rule.errors.append(f"Error during duplicate check: {str(e)}")
        rule.failed = len(df)
        return rule

def check_data_type(df: pd.DataFrame, column: str, expected_type: str) -> ValidationRule:
    """
    Check if column matches expected data type.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        expected_type: Expected data type (int, float, string, datetime)
    
    Returns:
        ValidationRule object with results
    """
    rule = ValidationRule("type_check", column)
    
    try:
        if column not in df.columns:
            rule.errors.append(f"Column '{column}' not found in DataFrame")
            rule.failed = len(df)
            return rule
        
        dtype_map = {
            'int': 'int64',
            'float': 'float64',
            'string': 'object',
            'datetime': 'datetime64'
        }
        
        actual_type = str(df[column].dtype)
        expected = dtype_map.get(expected_type.lower(), expected_type)
        
        if actual_type.startswith(expected):
            rule.passed = len(df)
            rule.failed = 0
        else:
            rule.passed = 0
            rule.failed = len(df)
            rule.errors.append(f"Expected type {expected_type}, but got {actual_type}")
        
        return rule
    
    except Exception as e:
        rule.errors.append(f"Error during type check: {str(e)}")
        rule.failed = len(df)
        return rule

def check_value_range(df: pd.DataFrame, column: str, min_val: float = None, max_val: float = None) -> ValidationRule:
    """
    Check if column values are within specified range.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        ValidationRule object with results
    """
    rule = ValidationRule("range_check", column)
    
    try:
        if column not in df.columns:
            rule.errors.append(f"Column '{column}' not found in DataFrame")
            rule.failed = len(df)
            return rule
        
        valid_rows = df[column]
        
        if min_val is not None:
            valid_rows = valid_rows[valid_rows >= min_val]
        
        if max_val is not None:
            valid_rows = valid_rows[valid_rows <= max_val]
        
        rule.passed = len(valid_rows)
        rule.failed = len(df) - rule.passed
        
        if rule.failed > 0:
            rule.errors.append(f"Found {rule.failed} values outside range [{min_val}, {max_val}]")
        
        return rule
    
    except Exception as e:
        rule.errors.append(f"Error during range check: {str(e)}")
        rule.failed = len(df)
        return rule

def check_schema(df: pd.DataFrame, expected_schema: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate DataFrame schema against expected columns and types.
    
    Args:
        df: DataFrame to validate
        expected_schema: Dictionary with column names as keys and expected types as values
                        Example: {"id": "int", "name": "string", "age": "float"}
    
    Returns:
        Dictionary with schema validation results
    """
    dtype_map = {
        'int': 'int64',
        'float': 'float64',
        'string': 'object',
        'datetime': 'datetime64',
        'bool': 'bool'
    }
    
    results = {
        "schema_valid": True,
        "missing_columns": [],
        "extra_columns": [],
        "type_mismatches": [],
        "errors": []
    }
    
    try:
        expected_columns = set(expected_schema.keys())
        actual_columns = set(df.columns)
        
        # Check for missing columns
        missing = expected_columns - actual_columns
        if missing:
            results["schema_valid"] = False
            results["missing_columns"] = list(missing)
            results["errors"].append(f"Missing columns: {', '.join(missing)}")
        
        # Check for extra columns
        extra = actual_columns - expected_columns
        if extra:
            results["extra_columns"] = list(extra)
        
        # Check for type mismatches
        for column, expected_type in expected_schema.items():
            if column in df.columns:
                actual_dtype = str(df[column].dtype)
                expected_dtype = dtype_map.get(expected_type.lower(), expected_type)
                
                if not actual_dtype.startswith(expected_dtype):
                    results["schema_valid"] = False
                    results["type_mismatches"].append({
                        "column": column,
                        "expected": expected_type,
                        "actual": actual_dtype
                    })
                    results["errors"].append(
                        f"Column '{column}': expected {expected_type}, got {actual_dtype}"
                    )
        
        return results
    
    except Exception as e:
        results["schema_valid"] = False
        results["errors"].append(f"Error during schema validation: {str(e)}")
        return results

def check_column_uniqueness(df: pd.DataFrame, column: str) -> ValidationRule:
    """
    Check if column contains all unique values (primary key validation).
    
    Args:
        df: DataFrame to validate
        column: Column name to check for uniqueness
    
    Returns:
        ValidationRule object with results
    """
    rule = ValidationRule("uniqueness_check", column)
    
    try:
        if column not in df.columns:
            rule.errors.append(f"Column '{column}' not found in DataFrame")
            rule.failed = len(df)
            return rule
        
        total_rows = len(df)
        unique_count = df[column].nunique()
        
        rule.passed = unique_count
        rule.failed = total_rows - unique_count
        
        if rule.failed > 0:
            rule.errors.append(f"Column '{column}' has {rule.failed} duplicate values")
        
        return rule
    
    except Exception as e:
        rule.errors.append(f"Error during uniqueness check: {str(e)}")
        rule.failed = len(df)
        return rule
