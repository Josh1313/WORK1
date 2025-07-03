from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from datetime import datetime


from ...schema.chat import ChatRequest, ChatResponse, ChatHistory
from ...services.chat import ChatService
from ...services.storage import StorageService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process a chat query about a dataset"""
    try:
        # Load dataset
        storage = StorageService()
        df = await storage.load_dataset(request.dataset_id)
        
        if df is None:
            raise HTTPException(404, "Dataset not found")
        
        # Process query
        chat_service = ChatService()
        response = await chat_service.process_query(
            df=df,
            query=request.query,
            context=request.context
        )
        
        return ChatResponse(
            response=response,
            dataset_id=request.dataset_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        raise HTTPException(500, f"Error processing query: {str(e)}")


@router.get("/history/{dataset_id}", response_model=ChatHistory)
async def get_chat_history(dataset_id: str):
    """Get chat history for a dataset"""
    storage = StorageService()
    history = await storage.get_chat_history(dataset_id)
    
    return ChatHistory(
        dataset_id=dataset_id,
        messages=history
    )

@router.delete("/history/{dataset_id}")
async def clear_chat_history(dataset_id: str):
    """Clear chat history for a dataset"""
    storage = StorageService()
    await storage.clear_chat_history(dataset_id)
    
    return {"message": "Chat history cleared"}