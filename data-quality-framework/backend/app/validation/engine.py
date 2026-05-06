import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.validation.rules import (
    check_null_values,
    check_duplicates,
    check_data_type,
    check_value_range,
    check_schema,
    check_column_uniqueness,
    ValidationRule
)

class ValidationEngine:
    def __init__(self, df: pd.DataFrame, dataset_name: str = ""):
        self.df = df
        self.dataset_name = dataset_name
        self.validation_results = []
        self.execution_timestamp = datetime.utcnow()
    
    def run_null_check(self, column: str, allow_null: bool = False) -> 'ValidationEngine':
        """Run null value check on a column."""
        result = check_null_values(self.df, column, allow_null)
        self.validation_results.append(result)
        return self
    
    def run_duplicate_check(self, column: str, allow_duplicates: bool = False) -> 'ValidationEngine':
        """Run duplicate value check on a column."""
        result = check_duplicates(self.df, column, allow_duplicates)
        self.validation_results.append(result)
        return self
    
    def run_type_check(self, column: str, expected_type: str) -> 'ValidationEngine':
        """Run data type check on a column."""
        result = check_data_type(self.df, column, expected_type)
        self.validation_results.append(result)
        return self
    
    def run_range_check(self, column: str, min_val: float = None, max_val: float = None) -> 'ValidationEngine':
        """Run value range check on a column."""
        result = check_value_range(self.df, column, min_val, max_val)
        self.validation_results.append(result)
        return self
    
    def run_uniqueness_check(self, column: str) -> 'ValidationEngine':
        """Run uniqueness check on a column."""
        result = check_column_uniqueness(self.df, column)
        self.validation_results.append(result)
        return self
    
    def run_schema_validation(self, expected_schema: Dict[str, str]) -> 'ValidationEngine':
        """Run schema validation."""
        result = check_schema(self.df, expected_schema)
        self.validation_results.append(result)
        return self
    
    def run_custom_check(self, rule_name: str, column: str, check_func) -> 'ValidationEngine':
        """Run a custom validation function."""
        try:
            result = check_func(self.df, column)
            if isinstance(result, ValidationRule):
                self.validation_results.append(result)
            else:
                self.validation_results.append({
                    "rule_name": rule_name,
                    "column": column,
                    "result": result
                })
        except Exception as e:
            self.validation_results.append({
                "rule_name": rule_name,
                "column": column,
                "error": str(e)
            })
        return self
    
    def get_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        rules_summary = []
        total_passed = 0
        total_failed = 0
        all_errors = []
        
        for result in self.validation_results:
            if isinstance(result, ValidationRule):
                summary = result.to_dict()
                rules_summary.append(summary)
                total_passed += result.passed
                total_failed += result.failed
                all_errors.extend(result.errors)
            elif isinstance(result, dict):
                if "errors" in result:
                    all_errors.extend(result["errors"])
                rules_summary.append(result)
        
        overall_pass_rate = round(
            (total_passed / (total_passed + total_failed) * 100), 2
        ) if (total_passed + total_failed) > 0 else 0
        
        return {
            "dataset_name": self.dataset_name,
            "execution_timestamp": self.execution_timestamp.isoformat(),
            "total_rules": len(self.validation_results),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "overall_pass_rate": overall_pass_rate,
            "validation_status": "PASSED" if total_failed == 0 else "FAILED",
            "rules": rules_summary,
            "errors": all_errors,
            "data_shape": {
                "rows": len(self.df),
                "columns": len(self.df.columns)
            }
        }
    
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        for result in self.validation_results:
            if isinstance(result, ValidationRule):
                if result.failed > 0:
                    return False
            elif isinstance(result, dict) and "schema_valid" in result:
                if not result["schema_valid"]:
                    return False
        return True
    
    def get_failed_rules(self) -> List[Dict[str, Any]]:
        """Get only failed validation rules."""
        failed = []
        for result in self.validation_results:
            if isinstance(result, ValidationRule) and result.failed > 0:
                failed.append(result.to_dict())
            elif isinstance(result, dict) and "schema_valid" in result and not result["schema_valid"]:
                failed.append(result)
        return failed

def create_validation_pipeline(
    df: pd.DataFrame,
    validations: List[Dict[str, Any]],
    dataset_name: str = ""
) -> Dict[str, Any]:
    """
    Execute a predefined validation pipeline.
    
    Args:
        df: DataFrame to validate
        validations: List of validation configurations
        dataset_name: Name of the dataset for reporting
    
    Returns:
        Validation report dictionary
    
    Example:
        validations = [
            {"type": "null_check", "column": "id", "allow_null": False},
            {"type": "type_check", "column": "age", "expected_type": "int"},
            {"type": "range_check", "column": "age", "min_val": 0, "max_val": 150}
        ]
    """
    engine = ValidationEngine(df, dataset_name)
    
    for validation in validations:
        v_type = validation.get("type")
        column = validation.get("column")
        
        try:
            if v_type == "null_check":
                engine.run_null_check(column, validation.get("allow_null", False))
            
            elif v_type == "duplicate_check":
                engine.run_duplicate_check(column, validation.get("allow_duplicates", False))
            
            elif v_type == "type_check":
                engine.run_type_check(column, validation.get("expected_type"))
            
            elif v_type == "range_check":
                engine.run_range_check(
                    column,
                    validation.get("min_val"),
                    validation.get("max_val")
                )
            
            elif v_type == "uniqueness_check":
                engine.run_uniqueness_check(column)
            
            elif v_type == "schema":
                engine.run_schema_validation(validation.get("schema", {}))
        
        except Exception as e:
            engine.validation_results.append({
                "rule_name": v_type,
                "column": column,
                "error": str(e)
            })
    
    return engine.get_report()
