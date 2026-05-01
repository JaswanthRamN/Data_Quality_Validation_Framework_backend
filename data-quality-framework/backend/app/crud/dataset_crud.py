from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.dataset import Dataset
from app.schemas.dataset_schema import DatasetCreate

def create_dataset(db: Session, dataset: DatasetCreate) -> Dataset:
    try:
        db_dataset = Dataset(name=dataset.name, source_type=dataset.source_type)
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        return db_dataset
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Dataset with this name already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating dataset")

def get_all_datasets(db: Session) -> list[Dataset]:
    try:
        return db.query(Dataset).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving datasets")

def get_dataset_by_id(db: Session, dataset_id: int) -> Dataset:
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving dataset")

def delete_dataset(db: Session, dataset_id: int) -> bool:
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        db.delete(dataset)
        db.commit()
        return True
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting dataset")
