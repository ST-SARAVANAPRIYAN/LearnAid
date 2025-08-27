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
        self.chunk_size = 1000  # Words per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
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
    
    async def process_pdf(self, file_path: str, extract_images: bool = False) -> PDFContent:
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
        """Split content into manageable chunks for processing"""
        chunks = []
        words = content.split()
        
        if not words:
            return chunks
        
        chunk_index = 0
        start_idx = 0
        
        while start_idx < len(words):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(words))
            
            # Extract chunk words
            chunk_words = words[start_idx:end_idx]
            chunk_content = " ".join(chunk_words)
            
            # Create chunk object
            chunk = ContentChunk(
                chunk_id=f"chunk_{chunk_index:03d}",
                content=chunk_content,
                page_number=self._estimate_page_number(chunk_content),
                chunk_index=chunk_index,
                word_count=len(chunk_words)
            )
            
            chunks.append(chunk)
            
            # Move start index with overlap
            start_idx = end_idx - self.chunk_overlap if end_idx < len(words) else end_idx
            chunk_index += 1
        
        logger.info(f"Created {len(chunks)} content chunks")
        return chunks
    
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

# Global instance
pdf_service = PDFProcessingService()
