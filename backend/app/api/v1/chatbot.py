"""
Chatbot API endpoints for student self-learning
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.services.chatbot_service import chatbot_service, ChatMessage, RAGResponse
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    course_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float

class DocumentIndexRequest(BaseModel):
    content: str
    source_file: str
    course_id: int
    chapter_name: str
    metadata: Optional[Dict[str, Any]] = {}

class ChatHistoryResponse(BaseModel):
    session_id: str
    student_id: int
    course_id: Optional[int]
    messages: List[Dict[str, Any]]
    created_at: str
    updated_at: str

# Initialize router
router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])

@router.post("/ask")
async def ask_chatbot(
    request: ChatMessageRequest,
    student_id: int,
    db: Session = Depends(get_db)
) -> ChatMessageResponse:
    """
    Ask the AI chatbot a question about course materials
    """
    try:
        # Start new session if needed
        if not request.session_id:
            session_id = await chatbot_service.start_new_session(student_id, request.course_id)
        else:
            session_id = request.session_id
        
        # Process the message through RAG pipeline
        rag_response: RAGResponse = await chatbot_service.process_message(
            session_id=session_id,
            user_message=request.message,
            student_id=student_id,
            course_id=request.course_id
        )
        
        # Convert sources to dict format
        sources = []
        for source in rag_response.sources:
            sources.append({
                'content': source.content,
                'score': source.score,
                'source_file': source.source_file,
                'chapter_name': source.chapter_name,
                'course_id': source.course_id
            })
        
        return ChatMessageResponse(
            session_id=session_id,
            message=request.message,
            response=rag_response.answer,
            sources=sources,
            confidence=rag_response.confidence,
            processing_time=rag_response.processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing chatbot request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
) -> ChatHistoryResponse:
    """
    Get chat history for a session
    """
    try:
        session = await chatbot_service.get_chat_history(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Convert messages to dict format
        messages = []
        for msg in session.messages:
            messages.append({
                'message_id': msg.message_id,
                'content': msg.content,
                'role': msg.role,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata
            })
        
        return ChatHistoryResponse(
            session_id=session.session_id,
            student_id=session.student_id,
            course_id=session.course_id,
            messages=messages,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.post("/start-session")
async def start_chat_session(
    student_id: int,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Start a new chat session
    """
    try:
        session_id = await chatbot_service.start_new_session(student_id, course_id)
        
        return JSONResponse({
            'success': True,
            'session_id': session_id,
            'message': 'Chat session started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/index-document")
async def index_document(
    request: DocumentIndexRequest,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Index a document for chatbot knowledge base
    """
    try:
        success = await vector_service.index_document(
            content=request.content,
            source_file=request.source_file,
            course_id=request.course_id,
            chapter_name=request.chapter_name,
            metadata=request.metadata
        )
        
        if success:
            return JSONResponse({
                'success': True,
                'message': f'Document {request.source_file} indexed successfully'
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to index document")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@router.get("/search")
async def search_documents(
    query: str,
    course_id: Optional[int] = None,
    k: int = 5,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Search for relevant documents (for testing purposes)
    """
    try:
        results = await vector_service.search_documents(
            query=query,
            course_id=course_id,
            k=k
        )
        
        search_results = []
        for result in results:
            search_results.append({
                'content': result.content,
                'score': result.score,
                'source_file': result.source_file,
                'chapter_name': result.chapter_name,
                'course_id': result.course_id,
                'metadata': result.metadata
            })
        
        return JSONResponse({
            'success': True,
            'query': query,
            'results': search_results,
            'total_found': len(search_results)
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")

@router.get("/analytics/session-summary/{session_id}")
async def get_session_summary(
    session_id: str,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Get analytics summary for a chat session
    """
    try:
        summary = await chatbot_service.get_conversation_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse({
            'success': True,
            'summary': summary
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session summary: {str(e)}")

@router.get("/analytics/popular-topics")
async def get_popular_topics(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Get analytics on popular topics and questions
    """
    try:
        topics = await chatbot_service.get_popular_topics(course_id)
        
        return JSONResponse({
            'success': True,
            'topics': topics,
            'course_id': course_id
        })
        
    except Exception as e:
        logger.error(f"Error getting popular topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get popular topics: {str(e)}")

@router.get("/vector-stats")
async def get_vector_database_stats(
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Get vector database statistics
    """
    try:
        stats = await vector_service.get_statistics()
        
        return JSONResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting vector database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/test-rag")
async def test_rag_pipeline(
    query: str,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Test the RAG pipeline (development/testing endpoint)
    """
    try:
        # Create a temporary session for testing
        session_id = await chatbot_service.start_new_session(student_id=1, course_id=course_id)
        
        # Process the query
        rag_response = await chatbot_service.process_message(
            session_id=session_id,
            user_message=query,
            student_id=1,
            course_id=course_id
        )
        
        # Format response
        sources = []
        for source in rag_response.sources:
            sources.append({
                'content': source.content[:200] + "..." if len(source.content) > 200 else source.content,
                'score': source.score,
                'source_file': source.source_file,
                'chapter_name': source.chapter_name,
                'course_id': source.course_id
            })
        
        return JSONResponse({
            'success': True,
            'query': query,
            'answer': rag_response.answer,
            'sources': sources,
            'confidence': rag_response.confidence,
            'processing_time': rag_response.processing_time,
            'test_session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error testing RAG pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"RAG pipeline test failed: {str(e)}")
