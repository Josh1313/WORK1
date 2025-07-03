from fastapi import APIRouter, UploadFile, File, HTTPException, Form, WebSocket
from typing import List, Optional
import pandas as pd
import io
import chardet
from datetime import datetime
import asyncio
import json

from ...services.storage import StorageService
from ...services.clustering import ClusteringService
from ...schema.file import FileInfo, FileUploadResponse, ClusteringRequest

router = APIRouter()
storage = StorageService()

# CREATE A SINGLE INSTANCE HERE:
clustering_service = ClusteringService()

# Existing endpoints remain the same...

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Upload a CSV or Excel file"""
    try:
        # Validate file extension
        if not any(file.filename.endswith(ext) for ext in ['.csv', '.xlsx']):
            raise HTTPException(400, "Only CSV and Excel files are supported")
        
        # Read file content ONCE
        content = await file.read()
        
        # Process based on file type
        if file.filename.endswith('.csv'):
            # Detect encoding
            encoding = chardet.detect(content)['encoding'] or 'utf-8'
            # Create DataFrame from content
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        else:
            # Excel file
            df = pd.read_excel(io.BytesIO(content))
        
        # Save to storage
        dataset_id = await storage.save_dataset(df, file.filename, description)
        
        return FileUploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            rows=len(df),
            columns=len(df.columns),
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")

@router.get("/list", response_model=List[FileInfo])
async def list_files():
    """List all uploaded files"""
    return await storage.list_datasets()

@router.get("/{dataset_id}/preview")
async def preview_file(dataset_id: str, rows: int = 5):
    """Preview a dataset"""
    df = await storage.load_dataset(dataset_id)
    if df is None:
        raise HTTPException(404, "Dataset not found")
    
    return {
        "data": df.head(rows).to_dict(orient="records"),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict()
    }

@router.delete("/{dataset_id}")
async def delete_file(dataset_id: str):
    """Delete a dataset"""
    success = await storage.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(404, "Dataset not found")
    
    return {"message": "Dataset deleted successfully"}

@router.get("/{dataset_id}/download")
async def download_file(dataset_id: str):
    """Download a dataset as CSV"""
    df = await storage.load_dataset(dataset_id)
    if df is None:
        raise HTTPException(404, "Dataset not found")
    
    # Convert to CSV
    csv_data = df.to_csv(index=False)
    
    return {
        "content": csv_data,
        "filename": f"{dataset_id}.csv"
    }

@router.post("/{dataset_id}/cluster")
async def start_clustering(dataset_id: str, request: ClusteringRequest):
    """Start clustering process for a dataset"""
    # Verify dataset exists
    df = await storage.load_dataset(dataset_id)
    if df is None:
        raise HTTPException(404, "Dataset not found")
    
    # Verify required columns
    if request.description_column not in df.columns:
        raise HTTPException(400, f"Column '{request.description_column}' not found in dataset")
    
    # Create task ID
    task_id = f"cluster_{dataset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # # Start clustering in background
    # clustering_service = ClusteringService()
    
    # CRITICAL: Register the task BEFORE starting background work
    await clustering_service.create_task(task_id, dataset_id)
    
    asyncio.create_task(
        clustering_service.process_clustering(
            task_id=task_id,
            dataset_id=dataset_id,
            df=df,
            description_column=request.description_column,
            number_column=request.number_column,
            n_clusters=request.n_clusters
        )
    )
    
    return {
        "task_id": task_id,
        "message": "Clustering process started",
        "status_endpoint": f"/api/files/cluster/status/{task_id}"
    }

@router.get("/cluster/status/{task_id}")
async def get_clustering_status(task_id: str):
    """Get status of clustering task"""
    status = await clustering_service.get_task_status(task_id)
    
    if status is None:
        raise HTTPException(404, "Task not found")
    
    return status

@router.websocket("/cluster/ws/{task_id}")
async def clustering_websocket(websocket: WebSocket, task_id: str):
    """WebSocket for real-time clustering updates"""
    await websocket.accept()
    clustering_service = ClusteringService()
    
    try:
        while True:
            status = await clustering_service.get_task_status(task_id)
            if status:
                await websocket.send_json(status)
                if status["status"] in ["completed", "failed"]:
                    break
            await asyncio.sleep(1)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()