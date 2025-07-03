from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatRequest(BaseModel):
    dataset_id: str
    query: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    dataset_id: str
    timestamp: datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatHistory(BaseModel):
    dataset_id: str
    messages: List[ChatMessage]