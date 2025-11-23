"""
ChromaDB client for vector storage and semantic search
"""

import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from utils.logger import logger
from utils.profiler import time_function
from config.settings import settings
from database.models import DocumentChunk

class ChromaDBClient:
    """ChromaDB client for vector storage"""
    
    def __init__(
        self, 
        db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB client
        
        Args:
            db_path: Path to ChromaDB database
            collection_name: Name of the collection
            embedding_model: Sentence transformer model for embeddings
        """
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        logger.info(f"🔄 Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        logger.info("✅ Embedding model loaded")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"✅ ChromaDB client initialized with collection: {self.collection_name}")
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    @time_function
    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Add document chunks to ChromaDB
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Number of chunks added
        """
        try:
            if not chunks:
                logger.warning("⚠️ No chunks to add")
                return 0
            
            # Prepare data
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.chunk_text for chunk in chunks]
            metadatas = [
                {
                    "document_name": chunk.document_name,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata
                }
                for chunk in chunks
            ]
            
            # Generate embeddings
            logger.info(f"🔄 Generating embeddings for {len(chunks)} chunks...")
            embeddings = self._generate_embeddings(texts)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Added {len(chunks)} chunks to ChromaDB")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Error adding chunks to ChromaDB: {e}")
            raise
    
    @time_function
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in ChromaDB
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with relevance scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embeddings([query])[0]
            
            # Search
            where = filter_metadata if filter_metadata else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "chunk_id": results['ids'][0][i],
                        "document_name": results['metadatas'][0][i].get('document_name', ''),
                        "chunk_text": results['documents'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None,
                        "metadata": results['metadatas'][0][i]
                    })
            
            logger.info(f"✅ Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching ChromaDB: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}
    
    def delete_collection(self):
        """Delete the collection (use with caution)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.warning(f"⚠️ Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ Error deleting collection: {e}")
    
    def clear_all_data(self):
        """
        Clear all data from ChromaDB collection
        WARNING: This will delete all chunks from the collection
        """
        try:
            # Get all IDs in the collection
            count = self.collection.count()
            if count == 0:
                logger.info("ℹ️ ChromaDB collection is already empty")
                return {"chunks_deleted": 0}
            
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.warning(f"⚠️ Cleared ChromaDB collection: {count} chunks deleted")
            return {"chunks_deleted": count}
        except Exception as e:
            logger.error(f"❌ Error clearing ChromaDB data: {e}")
            raise

__all__ = ["ChromaDBClient"]

