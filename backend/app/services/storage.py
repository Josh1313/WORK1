import os
import json
import aiosqlite
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import asyncio
import logging

from app.config import settings
from app.schema.file import FileInfo

logger = logging.getLogger(__name__)

class StorageService:
    """Handle all storage operations using SQLite"""
    
    def __init__(self):
        self.db_path = settings.data_dir / "app.db"
        self.datasets_dir = settings.data_dir / "datasets"
        
    async def initialize(self):
        """Initialize the storage system"""
        # Create directories
        self.datasets_dir.mkdir(exist_ok=True)
        
        # Initialize database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    columns INTEGER NOT NULL,
                    size_mb REAL NOT NULL,
                    description TEXT,
                    file_path TEXT NOT NULL
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (dataset_id)
                )
            """)
            
            await db.commit()
            
        logger.info("Storage system initialized")
    
    async def save_dataset(self, df: pd.DataFrame, filename: str, description: Optional[str] = None) -> str:
        """Save dataset to storage"""
        # Generate unique ID
        dataset_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename.replace('.', '_')}"
        file_path = self.datasets_dir / f"{dataset_id}.parquet"
        
        # Save DataFrame
        df.to_parquet(file_path, engine='pyarrow', index=False)
        
        # Save metadata
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO datasets (dataset_id, filename, upload_date, rows, columns, size_mb, description, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset_id,
                filename,
                datetime.now().isoformat(),
                len(df),
                len(df.columns),
                file_path.stat().st_size / (1024 * 1024),
                description,
                str(file_path)
            ))
            await db.commit()
        
        logger.info(f"Dataset saved: {dataset_id}")
        return dataset_id
    
    async def load_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Load dataset from storage"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT file_path FROM datasets WHERE dataset_id = ?",
                (dataset_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                file_path = Path(row[0])
                if file_path.exists():
                    return pd.read_parquet(file_path)
        
        return None
    
    async def list_datasets(self) -> List[FileInfo]:
        """List all datasets"""
        datasets = []
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT dataset_id, filename, upload_date, rows, columns, size_mb, description
                FROM datasets
                ORDER BY upload_date DESC
            """)
            
            async for row in cursor:
                datasets.append(FileInfo(
                    dataset_id=row[0],
                    filename=row[1],
                    upload_date=datetime.fromisoformat(row[2]),
                    rows=row[3],
                    columns=row[4],
                    size_mb=row[5],
                    description=row[6]
                ))
        
        return datasets
    
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset from storage"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get file path
            cursor = await db.execute(
                "SELECT file_path FROM datasets WHERE dataset_id = ?",
                (dataset_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Delete file
                file_path = Path(row[0])
                if file_path.exists():
                    file_path.unlink()
                
                # Delete from database
                await db.execute("DELETE FROM datasets WHERE dataset_id = ?", (dataset_id,))
                await db.execute("DELETE FROM chat_history WHERE dataset_id = ?", (dataset_id,))
                await db.commit()
                
                logger.info(f"Dataset deleted: {dataset_id}")
                return True
        
        return False
    
    async def save_chat_message(self, dataset_id: str, role: str, content: str):
        """Save chat message to history"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO chat_history (dataset_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (dataset_id, role, content, datetime.now().isoformat()))
            await db.commit()
    
    async def get_chat_history(self, dataset_id: str) -> List[dict]:
        """Get chat history for a dataset"""
        messages = []
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT role, content, timestamp
                FROM chat_history
                WHERE dataset_id = ?
                ORDER BY timestamp
            """, (dataset_id,))
            
            async for row in cursor:
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2]
                })
        
        return messages
    
    async def clear_chat_history(self, dataset_id: str):
        """Clear chat history for a dataset"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM chat_history WHERE dataset_id = ?", (dataset_id,))
            await db.commit()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Storage cleanup completed")
        
    # Add this method to the existing StorageService class

    async def get_dataset_filename(self, dataset_id: str) -> Optional[str]:
        """Get original filename for a dataset"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT filename FROM datasets WHERE dataset_id = ?",
                (dataset_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None    