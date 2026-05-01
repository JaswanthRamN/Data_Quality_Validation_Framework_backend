from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Dataset name")
    source_type: str = Field(..., min_length=1, max_length=100, description="Source type (csv, api, database, etc.)")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('name cannot be empty or whitespace')
        return v.strip()

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v):
        valid_types = ['csv', 'api', 'database', 'json', 'parquet']
        if v.lower() not in valid_types:
            raise ValueError(f'source_type must be one of {valid_types}')
        return v.lower()

class DatasetResponse(BaseModel):
    id: int
    name: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True
