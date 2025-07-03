from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class FileInfo(BaseModel):
    dataset_id: str
    filename: str
    upload_date: datetime
    rows: int
    columns: int
    size_mb: float
    description: Optional[str] = None

class FileUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    message: str

class ClusteringRequest(BaseModel):
    description_column: str
    number_column: Optional[str] = None
    n_clusters: int = 0  # 0 means auto-detect

class ClusteringStatus(BaseModel):
    task_id: str
    status: Literal["processing", "completed", "failed"]
    progress: int  # 0-100
    message: str
    result: Optional[str] = None  # dataset_id of result
    timestamp: datetime