import requests
from typing import Optional, List, Dict
import pandas as pd
import io
from config import config

class APIClient:
    """Client for backend API communication"""
    
    def __init__(self):
        self.base_url = config.BACKEND_URL
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check if backend is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.json()
        except:
            return {"status": "unhealthy", "message": "Cannot connect to backend"}
    
    def upload_file(self, file, filename: str, description: Optional[str] = None) -> Dict:
        """Upload a file to backend"""
        files = {"file": (filename, file, "application/octet-stream")}
        data = {"description": description} if description else {}
        
        response = self.session.post(
            f"{self.base_url}/api/files/upload",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_files(self) -> List[Dict]:
        """List all files"""
        response = self.session.get(f"{self.base_url}/api/files/list")
        response.raise_for_status()
        return response.json()
    
    def preview_file(self, dataset_id: str, rows: int = 5) -> Dict:
        """Preview a file"""
        response = self.session.get(
            f"{self.base_url}/api/files/{dataset_id}/preview",
            params={"rows": rows}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_file(self, dataset_id: str) -> Dict:
        """Delete a file"""
        response = self.session.delete(f"{self.base_url}/api/files/{dataset_id}")
        response.raise_for_status()
        return response.json()
    
    def download_file(self, dataset_id: str) -> Dict:
        """Download a file"""
        response = self.session.get(f"{self.base_url}/api/files/{dataset_id}/download")
        response.raise_for_status()
        return response.json()
    
    def chat_query(self, dataset_id: str, query: str, context: Optional[str] = None) -> Dict:
        """Send chat query"""
        payload = {
            "dataset_id": dataset_id,
            "query": query,
            "context": context
        }
        
        response = self.session.post(
            f"{self.base_url}/api/chat/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_chat_history(self, dataset_id: str) -> Dict:
        """Get chat history"""
        response = self.session.get(f"{self.base_url}/api/chat/history/{dataset_id}")
        response.raise_for_status()
        return response.json()
    
    def clear_chat_history(self, dataset_id: str) -> Dict:
        """Clear chat history"""
        response = self.session.delete(f"{self.base_url}/api/chat/history/{dataset_id}")
        response.raise_for_status()
        return response.json()
    

    def start_clustering(self, dataset_id: str, description_column: str, 
                        number_column: Optional[str] = None, n_clusters: int = 0) -> Dict:
        """Start clustering process"""
        payload = {
            "description_column": description_column,
            "number_column": number_column,
            "n_clusters": n_clusters
        }
        
        response = self.session.post(
            f"{self.base_url}/api/files/{dataset_id}/cluster",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_clustering_status(self, task_id: str) -> Dict:
        """Get clustering task status"""
        response = self.session.get(
            f"{self.base_url}/api/files/cluster/status/{task_id}"
        )
        response.raise_for_status()
        return response.json()

# Create global instance
api_client = APIClient()