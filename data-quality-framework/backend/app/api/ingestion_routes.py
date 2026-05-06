from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from datetime import datetime

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

DATA_SOURCES_DIR = Path("data_sources")
DATA_SOURCES_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Validate file extension
        allowed_extensions = ['.csv', '.json', '.parquet', '.xlsx', '.xls']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        unique_filename = timestamp + file.filename
        file_path = DATA_SOURCES_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "filename": file.filename,
            "saved_as": unique_filename,
            "file_path": str(file_path),
            "size": file_path.stat().st_size,
            "message": "File uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/files")
async def list_uploaded_files():
    try:
        files = list(DATA_SOURCES_DIR.glob("*"))
        file_list = [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_ctime)
            }
            for f in files if f.is_file()
        ]
        return {"files": file_list, "total": len(file_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
