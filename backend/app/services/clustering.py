import pandas as pd
import numpy as np
import re
import random
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import tiktoken
from openai import AsyncOpenAI
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score
from sklearn.utils import resample
from tqdm import tqdm

from app.config import settings
from app.services.storage import StorageService

logger = logging.getLogger(__name__)

class ClusteringService:
    def __init__(self):
        self.storage = StorageService()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.encoding = tiktoken.encoding_for_model("text-embedding-3-small")
        self.MAX_TOKENS = 8000
        # Initialize AsyncOpenAI client with new interface
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    # ADD THIS METHOD:
    async def create_task(self, task_id: str, dataset_id: str) -> Dict[str, Any]:
        """Create and register a new clustering task"""
        task_info = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "message": "Task created, preparing to start clustering...",
            "result": None,
            "timestamp": datetime.now().isoformat(),
            "dataset_id": dataset_id
        }
        
        # Register task immediately
        self.tasks[task_id] = task_info
        logger.info(f"Task {task_id} registered successfully")
        return task_info    
    
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a clustering task"""
        task = self.tasks.get(task_id)
        if task:
            logger.debug(f"Task {task_id} found - status: {task['status']}")
        else:
            logger.warning(f"Task {task_id} NOT FOUND. Available tasks: {list(self.tasks.keys())}")
        return task
    
    async def update_task_status(self, task_id: str, status: str, progress: int, 
                                message: str, result: Optional[str] = None):
        """Update task status"""
        self.tasks[task_id] = {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def clean_description(self, text: str) -> str:
        """Clean text description"""
        text = str(text).lower()
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove line breaks / tabs
        text = re.sub(r'[\r\n\t]', ' ', text)
        # Remove words with digits (e.g. device codes)
        text = re.sub(r'\b\w*\d\w*\b', ' ', text)
        # Remove all remaining non-alphanumerics
        text = re.sub(r'[^a-z ]+', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def count_tokens(self, texts):
        """Count tokens in texts"""
        return sum(len(self.encoding.encode(t)) for t in texts)
    
    async def calculate_optimal_batch_size(self, texts):
        """Calculate optimal batch size based on token analysis"""
        # Sample texts to estimate average tokens
        sample_size = min(100, len(texts))
        sample_texts = texts[:sample_size]
        
        # Calculate average tokens per text
        total_tokens = sum(len(self.encoding.encode(text)) for text in sample_texts)
        avg_tokens_per_text = total_tokens / len(sample_texts)
        
        # Calculate safe batch size (leave 10% buffer)
        safe_batch_size = int((self.MAX_TOKENS * 0.9) / avg_tokens_per_text)
        
        # Ensure reasonable bounds
        batch_size = max(1, min(safe_batch_size, 50))  # Between 1-50 texts per batch
        
        logger.info(f"Calculated optimal batch size: {batch_size} (avg tokens per text: {avg_tokens_per_text:.1f})")
        return batch_size
    
    async def embed_batch(self, texts, model="text-embedding-3-small", retries=2):
        """Embed a batch of texts"""
        # filter empty
        texts = [t if t is not None else "" for t in texts]
        # if too many tokens, split (this should rarely happen now)
        if self.count_tokens(texts) > self.MAX_TOKENS and len(texts) > 1:
            mid = len(texts) // 2
            emb1 = await self.embed_batch(texts[:mid], model)
            emb2 = await self.embed_batch(texts[mid:], model)
            return emb1 + emb2
        
        # try embedding
        for attempt in range(retries + 1):
            try:
                # Add small delay to respect rate limits
                if attempt > 0:
                    await asyncio.sleep(0.5)
                
                # Use new OpenAI 1.0+ interface
                response = await self.client.embeddings.create(
                    model=model,
                    input=texts
                )
                return [embedding.embedding for embedding in response.data]
            except Exception as e:
                if attempt < retries and len(texts) > 1:
                    try:
                        mid = len(texts) // 2
                        emb1 = await self.embed_batch(texts[:mid], model, retries)
                        emb2 = await self.embed_batch(texts[mid:], model, retries)
                        return emb1 + emb2
                    except Exception:
                        pass
                wait = 2 ** attempt
                logger.warning(f"[Attempt {attempt+1}] Error: {e}. Retrying in {wait}s...")
                if attempt < retries:
                    await asyncio.sleep(wait)
        
        raise RuntimeError(f"Batch embedding failed for {len(texts)} texts after {retries + 1} attempts")
    
    async def categorize_and_explain_cluster(self, records):
        """Generate cluster title and explanation using LLM"""
        sample_size = min(40, len(records))
        random_sample = random.sample(records, sample_size)
        text_sample = "\n".join(f"ID {r['number']}: {r['clean_desc']}" for r in random_sample)
        total_records = len(records)
        
        system_prompt = (
            "You are **ClusterNameBot**, an Business Consulting Assistant for ServiceNow.\n\n"  
            "Your job is to look at a batch of ticket descriptions all belonging to the same cluster and give that cluster.\n\n"
            "Please do the following:\n"
            "1. Assign a **short, descriptive title** for this cluster (2-5 words max).\n"
            "2. Do not use markdown just simple text.\n"
            "3. Give a brief explanation of **why** you chose this title, highlighting any recurring themes, language or keywords.\n\n"
            "Avoid generic names like 'Cluster 1' or 'Miscellaneous'. Make the title informative.\n\n"
            "Avoid duplicates titles names. Make the title informative.\n\n"
            "Format your output as:\n"
            "Title: <your title>\n"
            "Explanation: <your reasoning>\n"
            "Detailed Analysis: <common pain points and relationships>\n"
            "Five Top Issues: <reason with context given by the examples>"
        )

        user_prompt = (
            f"Total records received: {total_records}.\n\n"
            "Here are sample Records (Incident ID and description) from a single cluster:\n\n"
            f"{text_sample}\n\n"
            "Where possible, include in your explanation references to the incident IDs to indicate the source of your insights."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use new OpenAI 1.0+ interface
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    async def process_clustering(self, task_id: str, dataset_id: str, df: pd.DataFrame,
                               description_column: str, number_column: Optional[str],
                               n_clusters: int = 5):
        """Main clustering process"""
        try:
            # Step 1: Clean descriptions
            await self.update_task_status(task_id, "processing", 10, "Starting clustering analysis......")
            logger.info(f"Task {task_id}: Starting clustering for dataset {dataset_id}")
            
            df['clean_desc'] = df[description_column].apply(self.clean_description)
            df_clean = df.drop(columns=[description_column])
            
            # Drop empty descriptions
            mask = df_clean['clean_desc'].astype(str).str.strip() != ""
            df_clean = df_clean.loc[mask].reset_index(drop=True)
            
            # Step 2: Generate embeddings
            await self.update_task_status(task_id, "processing", 10, "Generating embeddings...")
            texts = df_clean['clean_desc'].tolist()
            # FIX: Calculate optimal batch size based on actual token counts
            batch_size = await self.calculate_optimal_batch_size(texts)
            all_embeddings = []
            
            total_batches = (len(texts) + batch_size - 1) // batch_size
            processed_batches = 0
            
            for start in range(0, len(texts), batch_size):
                batch = texts[start: start + batch_size]
                try:
                    embs = await self.embed_batch(batch)
                    all_embeddings.extend(embs)
                    logger.info(f"Successfully processed batch {processed_batches + 1}/{total_batches} with {len(batch)} texts")
                except Exception as e:
                    logger.error(f"Batch embedding failed: {e}")
                    # Use zero vectors as fallback
                    dim = len(all_embeddings[0]) if all_embeddings else 1536
                    all_embeddings.extend([[0.0] * dim for _ in batch])
                
                processed_batches += 1
                progress = 30 + int((processed_batches / total_batches) * 40)
                await self.update_task_status(
                    task_id, "processing", progress,
                    f"Generating embeddings... {processed_batches}/{total_batches} batches"
                )
            
            df_clean['embedding'] = all_embeddings
            
            # Step 3: Clustering
            await self.update_task_status(task_id, "processing", 65, "Performing clustering...")
            X = np.vstack(df_clean['embedding'].values)
            X_norm = normalize(X, norm='l2')
            
            # Find optimal clusters using silhouette score
            if n_clusters == 0:  # Auto-detect
                await self.update_task_status(task_id, "processing", 70, "Finding optimal clusters...")
                sil_scores = []
                sample_size = min(5000, len(X_norm))
                
                for k in range(2, min(11, len(X_norm))):
                    km = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = km.fit_predict(X_norm)
                    
                    X_sample, labels_sample = resample(X_norm, labels, n_samples=sample_size, random_state=42)
                    score = silhouette_score(X_sample, labels_sample)
                    sil_scores.append((k, score))
                
                # Choose k with highest silhouette score
                n_clusters = max(sil_scores, key=lambda x: x[1])[0]
                logger.info(f"Auto-detected optimal clusters: {n_clusters}")
            
            # Perform final clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_norm)
            df_clean['cluster'] = labels
            
            ## Step 4: Save intermediate clustering data as parquet to preserve data types
            await self.update_task_status(task_id, "processing", 75, "Saving intermediate clustering data...")
            
            # Generate intermediate parquet filename
            original_filename = await self.storage.get_dataset_filename(dataset_id)
            intermediate_filename = f"clustering_intermediate_{original_filename.replace('.csv', '.parquet')}"
            
            # Save as parquet to preserve embeddings and cluster data
            parquet_path = f"data/{intermediate_filename}"
            df_clean.to_parquet(parquet_path, index=False)
            logger.info(f"Saved intermediate clustering data to {parquet_path}")
            
            # Step 5: Generate cluster explanations
            await self.update_task_status(task_id, "processing", 80, "Generating cluster insights...")
            
            # Use number_column if provided, otherwise use index
            if number_column and number_column in df_clean.columns:
                id_column = number_column
            else:
                df_clean['number'] = df_clean.index
                id_column = 'number'
            
            cluster_summaries = {}
            total_clusters = len(df_clean['cluster'].unique())
            processed_clusters = 0
            
            for cluster_label in sorted(df_clean['cluster'].unique()):
                records = df_clean[df_clean['cluster'] == cluster_label][[id_column, 'clean_desc']].to_dict('records')
                summary_text = await self.categorize_and_explain_cluster(records)
                
                # Parse response
                title_match = re.search(r'Title:\s*(.*?)\n', summary_text)
                explanation_match = re.search(r'Explanation:\s*(.*?)(?=\n(?:Detailed Analysis:|Five Top Issues:|$))', 
                                            summary_text, re.DOTALL)
                detailed_match = re.search(r'Detailed Analysis:\s*(.*?)(?=\n(?:Five Top Issues:|$))', 
                                         summary_text, re.DOTALL)
                issues_match = re.search(r'Five Top Issues:\s*(.*)', summary_text, re.DOTALL)
                
                cluster_summaries[cluster_label] = {
                    'title': title_match.group(1).strip() if title_match else f'Cluster {cluster_label}',
                    'explanation': explanation_match.group(1).strip() if explanation_match else 'N/A',
                    'detailed_analysis': detailed_match.group(1).strip() if detailed_match else 'N/A',
                    'Five_Top_Issues': issues_match.group(1).strip() if issues_match else 'N/A'
                }
                
                processed_clusters += 1
                progress = 80 + int((processed_clusters / total_clusters) * 15)
                await self.update_task_status(
                    task_id, "processing", progress,
                    f"Analyzing clusters... {processed_clusters}/{total_clusters}"
                )
            
            # Map summaries back to dataframe
            df_clean['cluster_title'] = df_clean['cluster'].map(lambda x: cluster_summaries[x]['title'])
            df_clean['cluster_explanation'] = df_clean['cluster'].map(lambda x: cluster_summaries[x]['explanation'])
            df_clean['detailed_analysis'] = df_clean['cluster'].map(lambda x: cluster_summaries[x]['detailed_analysis'])
            df_clean['Five_Top_Issues'] = df_clean['cluster'].map(lambda x: cluster_summaries[x]['Five_Top_Issues'])
            
            # Step 6: Prepare final dataset by removing embeddings column for CSV export
            await self.update_task_status(task_id, "processing", 95, "Preparing final results...")
            
            # Remove embedding column for final CSV (keep all other cluster data)
            df_final = df_clean.drop(columns=['embedding'])
            
            # Generate filename
            #original_filename = await self.storage.get_dataset_filename(dataset_id)
            result_filename = f"clustered_{original_filename}"
            result_dataset_id = await self.storage.save_dataset(
                df_clean, 
                result_filename,
                f"Clustered analysis of {original_filename} with {n_clusters} clusters"
            )
            
            # Complete
            await self.update_task_status(
                task_id, "completed", 100,
                f"Clustering completed! Found {n_clusters} clusters.",
                result_dataset_id
            )
            
            logger.info(f"Task {task_id}: Clustering completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id}: Clustering failed - {str(e)}")
            await self.update_task_status(
                task_id, "failed", 0,
                f"Clustering failed: {str(e)}"
            )

