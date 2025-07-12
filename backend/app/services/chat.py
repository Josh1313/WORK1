import os
from typing import Optional
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

load_dotenv ()


from app.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    """Handle chat/LLM operations"""
    
    def __init__(self):
        self.model = AzureChatOpenAI(
            model=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            openai_api_key=settings.azure_openai_api_key,
            temperature=0.1
        )
        
        self.prompt_prefix = """
        You are a data analysis expert working with a pandas DataFrame called 'df'.
        
        When answering questions:
        1. Always begin by examining the DataFrame structure (columns, data types, basic stats)
        2. Write clear, executable Python code
        3. Execute your code and base your answers on the results
        """
        
        self.prompt_suffix = """
        Make your answer helpful and informative. Format numbers over 1,000 with commas.
        Also answer base on the input language of the user.
        Use emojis sparingly to enhance excitement (no more than 2). Keep it helpful, fun, and clear. 
        Avoid flat, robotic phrasing.
        """
    
    async def process_query(self, df: pd.DataFrame, query: str, context: Optional[str] = None) -> str:
        """Process a query about the dataframe"""
        try:
            # Create agent
            agent = create_pandas_dataframe_agent(
                llm=self.model,
                df=df,
                verbose=False,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True
            )
            
            # Build full query with context
            full_query = self.prompt_prefix + "\n"
            if context:
                full_query += f"Context: {context}\n"
            full_query += query + "\n" + self.prompt_suffix
            
            
            # Execute query
            response = agent.invoke({"input": full_query})
            
            return response["output"]
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise