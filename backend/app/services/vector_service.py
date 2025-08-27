"""
Vector Database Service for document embeddings and semantic search
"""
import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

# Vector database imports
try:
    import faiss
    import chromadb
    from chromadb.config import Settings
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    logging.warning("Vector database libraries not available. Install faiss-cpu and chromadb.")

# Embedding imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logging.warning("Sentence transformers not available. Install sentence-transformers.")

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DocumentChunk(BaseModel):
    """Represents a chunk of document content"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_file: str
    course_id: int
    chapter_name: str

class SearchResult(BaseModel):
    """Search result with relevance score"""
    content: str
    metadata: Dict[str, Any]
    score: float
    source_file: str
    course_id: int
    chapter_name: str

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        self.model_name = model_name
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        if not EMBEDDING_AVAILABLE:
            logger.error("Sentence transformers not available")
            return
        
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model '{self.model_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
    
    def encode_text(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not self.model:
            logger.error("Embedding model not available")
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return np.array([])
    
    def encode_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.encode_text([text])[0] if self.model else np.array([])

class FAISSVectorStore:
    """FAISS-based vector store for fast similarity search"""
    
    def __init__(self, dimension: int = 384, index_path: str = "vector_db/faiss_index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index = None
        self.metadata = {}
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index"""
        if not VECTOR_DB_AVAILABLE:
            logger.error("FAISS not available")
            return
        
        try:
            # Create directory if it doesn't exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to load existing index
            if self.index_path.with_suffix('.index').exists():
                self.index = faiss.read_index(str(self.index_path.with_suffix('.index')))
                # Load metadata
                metadata_path = self.index_path.with_suffix('.metadata')
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        self.metadata = json.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
                
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
    
    def add_documents(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        """Add document chunks to the vector store"""
        if not self.index:
            logger.error("FAISS index not available")
            return
        
        try:
            # Add embeddings to index
            self.index.add(embeddings.astype(np.float32))
            
            # Store metadata
            start_id = len(self.metadata)
            for i, chunk in enumerate(chunks):
                self.metadata[start_id + i] = {
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'chunk_id': chunk.chunk_id,
                    'source_file': chunk.source_file,
                    'course_id': chunk.course_id,
                    'chapter_name': chunk.chapter_name
                }
            
            logger.info(f"Added {len(chunks)} documents to FAISS index")
            self._save_index()
            
        except Exception as e:
            logger.error(f"Failed to add documents to FAISS index: {e}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[SearchResult]:
        """Search for similar documents"""
        if not self.index or self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        try:
            # Perform search
            scores, indices = self.index.search(
                query_embedding.reshape(1, -1).astype(np.float32), k
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx in self.metadata:
                    meta = self.metadata[idx]
                    results.append(SearchResult(
                        content=meta['content'],
                        metadata=meta['metadata'],
                        score=float(score),
                        source_file=meta['source_file'],
                        course_id=meta['course_id'],
                        chapter_name=meta['chapter_name']
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search FAISS index: {e}")
            return []
    
    def _save_index(self):
        """Save the FAISS index to disk"""
        try:
            faiss.write_index(self.index, str(self.index_path.with_suffix('.index')))
            # Save metadata
            with open(self.index_path.with_suffix('.metadata'), 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info("FAISS index saved successfully")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

class VectorStoreService:
    """Main service for vector database operations"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_service = EmbeddingService(embedding_model)
        self.vector_store = FAISSVectorStore()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk.strip())
            
            if end == len(text):
                break
                
            start = end - overlap
        
        return chunks
    
    async def index_document(
        self, 
        content: str, 
        source_file: str, 
        course_id: int, 
        chapter_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Index a document in the vector store"""
        try:
            # Chunk the content
            chunks = self.chunk_text(content)
            
            # Create document chunks
            doc_chunks = []
            for i, chunk_content in enumerate(chunks):
                chunk_meta = metadata or {}
                chunk_meta.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                
                doc_chunks.append(DocumentChunk(
                    content=chunk_content,
                    metadata=chunk_meta,
                    chunk_id=f"{source_file}_chunk_{i}",
                    source_file=source_file,
                    course_id=course_id,
                    chapter_name=chapter_name
                ))
            
            # Generate embeddings
            chunk_texts = [chunk.content for chunk in doc_chunks]
            embeddings = self.embedding_service.encode_text(chunk_texts)
            
            if embeddings.size == 0:
                logger.error("Failed to generate embeddings")
                return False
            
            # Add to vector store
            self.vector_store.add_documents(doc_chunks, embeddings)
            logger.info(f"Successfully indexed document: {source_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {source_file}: {e}")
            return False
    
    async def search_documents(
        self, 
        query: str, 
        course_id: Optional[int] = None,
        k: int = 5
    ) -> List[SearchResult]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode_single(query)
            
            if query_embedding.size == 0:
                logger.error("Failed to generate query embedding")
                return []
            
            # Perform search
            results = self.vector_store.search(query_embedding, k * 2)  # Get more for filtering
            
            # Filter by course_id if specified
            if course_id:
                results = [r for r in results if r.course_id == course_id]
            
            # Return top k results
            return results[:k]
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            total_docs = self.vector_store.index.ntotal if self.vector_store.index else 0
            
            # Count by course
            course_counts = {}
            for meta in self.vector_store.metadata.values():
                course_id = meta.get('course_id')
                course_counts[course_id] = course_counts.get(course_id, 0) + 1
            
            return {
                'total_chunks': total_docs,
                'courses_indexed': len(course_counts),
                'course_distribution': course_counts,
                'embedding_model': self.embedding_service.model_name,
                'vector_dimension': self.vector_store.dimension
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

# Global instance
vector_service = VectorStoreService()
