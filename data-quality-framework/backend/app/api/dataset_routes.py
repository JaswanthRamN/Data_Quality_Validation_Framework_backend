from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.dataset_crud import create_dataset, get_all_datasets, get_dataset_by_id, delete_dataset
from app.schemas.dataset_schema import DatasetCreate, DatasetResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/", response_model=DatasetResponse)
def create_new_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    return create_dataset(db, dataset)

@router.get("/", response_model=list[DatasetResponse])
def list_all_datasets(db: Session = Depends(get_db)):
    return get_all_datasets(db)

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    return get_dataset_by_id(db, dataset_id)

@router.delete("/{dataset_id}")
def remove_dataset(dataset_id: int, db: Session = Depends(get_db)):
    delete_dataset(db, dataset_id)
    return {"message": "Dataset deleted successfully"}
