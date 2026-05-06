import pandas as pd
from pathlib import Path
from fastapi import HTTPException
from typing import Optional

def read_csv_file(file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
    try:
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {str(e)}")

def read_csv_with_options(
    file_path: str, 
    delimiter: str = ',', 
    encoding: str = 'utf-8',
    skip_rows: Optional[int] = None,
    nrows: Optional[int] = None
) -> pd.DataFrame:
    try:
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        df = pd.read_csv(
            file_path, 
            delimiter=delimiter, 
            encoding=encoding,
            skiprows=skip_rows,
            nrows=nrows
        )
        return df
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {str(e)}")

def get_csv_metadata(file_path: str) -> dict:
    try:
        df = read_csv_file(file_path)
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV metadata: {str(e)}")
