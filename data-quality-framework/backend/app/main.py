from fastapi import FastAPI
from app.api.dataset_routes import router as dataset_router
from app.database import create_tables

app = FastAPI()

# Create all database tables
create_tables()

app.include_router(dataset_router)

@app.get("/")
def read_root():
    return {"message": "Data Quality Framework API"}
