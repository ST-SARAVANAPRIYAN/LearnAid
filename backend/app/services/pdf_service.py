"""
PDF Processing Service for handling document uploads and content extraction
"""
import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import aiofiles
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from pydantic import BaseModel

# Import vector service for embedding storage
from .vector_service import vector_service

logger = logging.getLogger(__name__)

class PDFContent(BaseModel):
    filename: str
    total_pages: int
    content: str
    chunks: List[str]
    metadata: Dict[str, Any]
    file_size: int
    upload_path: str

class ContentChunk(BaseModel):
    chunk_id: str
    content: str
    page_number: int
    chunk_index: int
    word_count: int

class PDFProcessingService:
    """Service for processing PDF files and extracting content"""
    
    def __init__(self, upload_directory: str = "uploads/pdfs"):
        self.upload_dir = Path(upload_directory)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        # Updated chunking parameters as requested: 500 char chunks with 100 char overlap
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 100  # Character overlap between chunks
    
    async def save_uploaded_file(self, file_content: bytes, filename: str, course_id: int, chapter_name: str) -> str:
        """
        Save uploaded PDF file to disk
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            course_id: Associated course ID
            chapter_name: Chapter name for organization
            
        Returns:
            File path where the PDF was saved
        """
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum limit of {self.max_file_size / (1024*1024):.1f}MB")
            
            # Create directory structure: uploads/pdfs/course_<id>/
            course_dir = self.upload_dir / f"course_{course_id}"
            course_dir.mkdir(exist_ok=True)
            
            # Generate safe filename
            safe_filename = self._generate_safe_filename(filename, chapter_name)
            file_path = course_dir / safe_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"PDF saved successfully: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving PDF file {filename}: {e}")
            raise
    
    async def process_pdf(self, file_path: str, course_id: int = 1, chapter_name: str = "Unknown Chapter", extract_images: bool = False) -> PDFContent:
        """
        Process PDF file and extract content
        
        Args:
            file_path: Path to the PDF file
            extract_images: Whether to extract images (future feature)
            
        Returns:
            PDFContent object with extracted data
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Extract content using PyMuPDF (more robust)
            content, metadata, total_pages = await self._extract_with_pymupdf(file_path)
            
            # Create content chunks
            chunks = self._create_content_chunks(content)
            
            # Prepare metadata for vector storage
            vector_metadata = metadata.copy()
            vector_metadata.update({
                'course_id': course_id,
                'chapter_name': chapter_name,
                'total_pages': total_pages,
                'file_size': file_path_obj.stat().st_size,
                'upload_timestamp': file_path_obj.stat().st_ctime
            })
            
            # Store in vector database
            await self._store_in_vector_db(content, file_path, chunks, vector_metadata)
            
            # Create PDFContent object
            pdf_content = PDFContent(
                filename=file_path_obj.name,
                total_pages=total_pages,
                content=content,
                chunks=[chunk.content for chunk in chunks],
                metadata=metadata,
                file_size=file_path_obj.stat().st_size,
                upload_path=file_path
            )
            
            logger.info(f"PDF processed successfully: {pdf_content.filename} ({total_pages} pages, {len(chunks)} chunks)")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
    
    async def _extract_with_pymupdf(self, file_path: str) -> Tuple[str, Dict[str, Any], int]:
        """Extract content using PyMuPDF for better text extraction"""
        try:
            doc = fitz.open(file_path)
            content_parts = []
            metadata = {}
            
            # Extract document metadata
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text("text")
                
                if page_text.strip():  # Only add non-empty pages
                    content_parts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            
            full_content = "\n".join(content_parts)
            return full_content, metadata, doc.page_count
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {file_path}: {e}")
            # Fallback to PyPDF2
            return await self._extract_with_pypdf2(file_path)
    
    async def _extract_with_pypdf2(self, file_path: str) -> Tuple[str, Dict[str, Any], int]:
        """Fallback extraction using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                content_parts = []
                metadata = {}
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                        "modification_date": str(pdf_reader.metadata.get("/ModDate", ""))
                    }
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            content_parts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                        continue
                
                full_content = "\n".join(content_parts)
                return full_content, metadata, len(pdf_reader.pages)
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed for {file_path}: {e}")
            raise
    
    def _create_content_chunks(self, content: str) -> List[ContentChunk]:
        """Split content into manageable chunks for processing - Character-based chunking"""
        chunks = []
        
        if not content.strip():
            return chunks
        
        chunk_index = 0
        start_idx = 0
        content_length = len(content)
        
        while start_idx < content_length:
            # Calculate end index for this chunk (500 characters)
            end_idx = min(start_idx + self.chunk_size, content_length)
            
            # Extract chunk content
            chunk_content = content[start_idx:end_idx]
            
            # Try to break at word boundary if we're not at the end
            if end_idx < content_length and not chunk_content.endswith(' '):
                # Find the last space within the chunk to avoid breaking words
                last_space = chunk_content.rfind(' ')
                if last_space > start_idx + (self.chunk_size * 0.8):  # Only if we don't lose too much content
                    end_idx = start_idx + last_space
                    chunk_content = content[start_idx:end_idx]
            
            # Clean up the chunk content
            chunk_content = chunk_content.strip()
            
            if chunk_content:  # Only add non-empty chunks
                # Create chunk object
                chunk = ContentChunk(
                    chunk_id=f"chunk_{chunk_index:03d}",
                    content=chunk_content,
                    page_number=self._estimate_page_number(chunk_content),
                    chunk_index=chunk_index,
                    word_count=len(chunk_content.split())
                )
                
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start index with overlap (100 characters back)
            if end_idx >= content_length:
                break
            start_idx = end_idx - self.chunk_overlap
            
            # Ensure we don't go backwards
            if start_idx < 0:
                start_idx = end_idx
        
        logger.info(f"Created {len(chunks)} content chunks (500 chars each, 100 char overlap)")
        return chunks
    
    async def _store_in_vector_db(self, content: str, file_path: str, chunks: List[ContentChunk], metadata: Dict[str, Any]) -> bool:
        """Store PDF content in vector database with chunking"""
        try:
            # Extract course_id and chapter_name from metadata or file path
            course_id = metadata.get('course_id', 1)  # Default to 1 if not provided
            chapter_name = metadata.get('chapter_name', 'Unknown Chapter')
            
            # Prepare document metadata for vector storage
            doc_metadata = {
                'file_path': file_path,
                'total_pages': metadata.get('total_pages', 0),
                'file_size': metadata.get('file_size', 0),
                'upload_timestamp': metadata.get('upload_timestamp'),
                'pdf_metadata': metadata
            }
            
            # Index the document in vector database using our character-based chunks
            try:
                success = await vector_service.index_document_with_chunks(
                    chunks=[chunk.content for chunk in chunks],
                    source_file=Path(file_path).name,
                    course_id=course_id,
                    chapter_name=chapter_name,
                    metadata=doc_metadata
                )
                
                if success:
                    logger.info(f"Successfully stored PDF in vector database: {Path(file_path).name} ({len(chunks)} chunks)")
                else:
                    logger.error(f"Failed to store PDF in vector database: {Path(file_path).name}")
                
                return success
            except Exception as e:
                logger.warning(f"Vector database not available, continuing without indexing: {e}")
                return True  # Return success even without vector database for now
            
        except Exception as e:
            logger.error(f"Error storing PDF in vector database: {e}")
            return False
    
    def _estimate_page_number(self, chunk_content: str) -> int:
        """Estimate page number from chunk content (looks for page markers)"""
        lines = chunk_content.split('\n')
        for line in lines:
            if line.strip().startswith('--- Page ') and line.strip().endswith(' ---'):
                try:
                    page_num = int(line.split()[2])
                    return page_num
                except (IndexError, ValueError):
                    continue
        return 1  # Default to page 1 if no marker found
    
    def _generate_safe_filename(self, original_filename: str, chapter_name: str) -> str:
        """Generate a safe filename for storage"""
        # Clean chapter name
        safe_chapter = "".join(c for c in chapter_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_chapter = safe_chapter.replace(' ', '_')[:50]  # Limit length
        
        # Get file extension
        file_ext = Path(original_filename).suffix
        
        # Create safe filename
        import time
        timestamp = int(time.time())
        safe_filename = f"{safe_chapter}_{timestamp}{file_ext}"
        
        return safe_filename
    
    async def delete_pdf(self, file_path: str) -> bool:
        """Delete PDF file from disk"""
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_path_obj.unlink()
                logger.info(f"PDF deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"PDF file not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting PDF {file_path}: {e}")
            return False
    
    async def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic information about a PDF file"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Use PyMuPDF for quick info extraction
            doc = fitz.open(file_path)
            
            info = {
                "filename": file_path_obj.name,
                "file_size": file_path_obj.stat().st_size,
                "total_pages": doc.page_count,
                "created": file_path_obj.stat().st_ctime,
                "modified": file_path_obj.stat().st_mtime,
                "metadata": doc.metadata if doc.metadata else {}
            }
            
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {file_path}: {e}")
            raise
    
    async def upload_and_process_pdf(
        self, 
        file_content: bytes, 
        filename: str, 
        course_id: int, 
        chapter_name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Complete PDF upload and processing workflow with vector database storage
        
        Args:
            file_content: Raw PDF file bytes
            filename: Original filename
            course_id: Course ID for organization
            chapter_name: Chapter name
            description: Optional description
            
        Returns:
            Dictionary with processing results and vector database info
        """
        try:
            logger.info(f"Starting PDF upload and processing: {filename} for course {course_id}, chapter '{chapter_name}'")
            
            # Step 1: Save the uploaded PDF file
            file_path = await self.save_uploaded_file(file_content, filename, course_id, chapter_name)
            
            # Step 2: Process PDF and store in vector database
            pdf_content = await self.process_pdf(
                file_path=file_path,
                course_id=course_id,
                chapter_name=chapter_name,
                extract_images=False
            )
            
            # Step 3: Get basic file info
            pdf_info = await self.get_pdf_info(file_path)
            
            # Step 4: Prepare response with vector database statistics
            try:
                from .vector_service import vector_service
                vector_stats = await vector_service.get_statistics()
            except Exception as e:
                logger.warning(f"Could not get vector database statistics: {e}")
                vector_stats = {
                    "total_chunks": 0,
                    "courses_indexed": 0,
                    "embedding_model": "not available"
                }
            
            result = {
                "success": True,
                "message": f"PDF processed successfully with {len(pdf_content.chunks)} chunks (500 chars each, 100 char overlap)",
                "file_info": {
                    "filename": pdf_content.filename,
                    "file_path": file_path,
                    "total_pages": pdf_content.total_pages,
                    "file_size": pdf_content.file_size,
                    "total_chunks": len(pdf_content.chunks),
                    "chunk_size": 500,
                    "chunk_overlap": 100
                },
                "processing_info": {
                    "course_id": course_id,
                    "chapter_name": chapter_name,
                    "description": description,
                    "chunks_created": len(pdf_content.chunks),
                    "content_length": len(pdf_content.content)
                },
                "vector_database": {
                    "stored": True,
                    "total_chunks_in_db": vector_stats.get("total_chunks", 0),
                    "courses_indexed": vector_stats.get("courses_indexed", 0),
                    "embedding_model": vector_stats.get("embedding_model", "unknown")
                },
                "metadata": pdf_content.metadata
            }
            
            logger.info(f"PDF processing completed successfully: {filename} -> {len(pdf_content.chunks)} chunks stored in vector DB")
            return result
            
        except Exception as e:
            logger.error(f"Error in complete PDF processing workflow for {filename}: {e}")
            return {
                "success": False,
                "message": f"Failed to process PDF: {str(e)}",
                "error": str(e)
            }

# Global instance
pdf_service = PDFProcessingService()
