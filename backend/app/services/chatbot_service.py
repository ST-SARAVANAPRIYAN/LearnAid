"""
Chatbot Service for AI-powered educational assistance using RAG
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel

from app.services.llm_service import GroqLLMService
from app.services.vector_service import VectorStoreService, SearchResult

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    """Represents a chat message"""
    message_id: str
    content: str
    role: str  # "user" or "assistant"
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = {}

class ChatSession(BaseModel):
    """Represents a chat session"""
    session_id: str
    student_id: int
    course_id: Optional[int]
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime

class RAGResponse(BaseModel):
    """Response from RAG pipeline"""
    answer: str
    sources: List[SearchResult]
    confidence: float
    processing_time: float

class ChatbotService:
    """Main chatbot service with RAG capabilities"""
    
    def __init__(self):
        self.llm_service = GroqLLMService()
        self.vector_service = VectorStoreService()
        self.active_sessions: Dict[str, ChatSession] = {}
        
    def _generate_system_prompt(self, context_docs: List[SearchResult], user_question: str) -> str:
        """Generate system prompt with retrieved context"""
        
        if not context_docs:
            return """You are an AI educational assistant. The user is asking a question about their course material, 
            but no specific context was found. Please provide a helpful general response and suggest they ask more specific questions."""
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(context_docs):
            context_parts.append(f"""
Context {i+1} (from {doc.chapter_name}):
{doc.content}
---""")
        
        context_text = "\n".join(context_parts)
        
        system_prompt = f"""You are an AI educational assistant helping a student with their coursework. 
You have access to the following relevant course material to answer their question:

{context_text}

Instructions:
1. Answer the student's question using ONLY the information provided in the context above
2. If the context doesn't contain enough information to fully answer the question, say so clearly
3. Be specific and educational in your response
4. Reference which part of the course material (chapter) you're drawing from
5. If applicable, provide examples or explanations to help the student understand better
6. Keep your response concise but thorough
7. If the student asks about something not covered in the provided context, politely redirect them to ask about topics covered in their course materials

Student's Question: {user_question}

Please provide a helpful, accurate response based on the course material provided."""

        return system_prompt
    
    async def process_message(
        self, 
        session_id: str,
        user_message: str,
        student_id: int,
        course_id: Optional[int] = None
    ) -> RAGResponse:
        """Process a user message through the RAG pipeline"""
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Searching for relevant documents for query: {user_message}")
            search_results = await self.vector_service.search_documents(
                query=user_message,
                course_id=course_id,
                k=3  # Top 3 most relevant chunks
            )
            
            # Step 2: Generate system prompt with context
            system_prompt = self._generate_system_prompt(search_results, user_message)
            
            # Step 3: Generate response using LLM
            logger.info("Generating AI response")
            
            # For now, simulate the LLM response since we don't have a real API key
            if not self.llm_service.client or "placeholder" in str(self.llm_service.client.api_key):
                ai_response = self._generate_mock_response(search_results, user_message)
            else:
                # Use actual Groq API
                try:
                    response = self.llm_service.client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    ai_response = response.choices[0].message.content
                except Exception as e:
                    logger.error(f"LLM API call failed: {e}")
                    ai_response = self._generate_mock_response(search_results, user_message)
            
            # Step 4: Calculate confidence based on search results quality
            confidence = self._calculate_confidence(search_results, user_message)
            
            # Step 5: Update chat session
            await self._update_chat_session(session_id, student_id, course_id, user_message, ai_response)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RAGResponse(
                answer=ai_response,
                sources=search_results,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            # Return error response
            return RAGResponse(
                answer="I'm sorry, I encountered an error while processing your question. Please try asking again or rephrase your question.",
                sources=[],
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _generate_mock_response(self, search_results: List[SearchResult], user_message: str) -> str:
        """Generate a mock AI response for demonstration purposes"""
        if not search_results:
            return """I understand you have a question about your course material. However, I couldn't find specific content related to your question in the uploaded course materials. 

Could you please:
1. Ask a more specific question about the topics covered in your course
2. Make sure the relevant course materials have been uploaded by your instructor
3. Try rephrasing your question using keywords from your syllabus

I'm here to help you learn from your course materials!"""

        # Create a response based on the search results
        primary_source = search_results[0]
        
        response = f"""Based on your course material from **{primary_source.chapter_name}**, I can help answer your question.

{primary_source.content[:200]}...

This information relates to your question about: "{user_message}"

**Key Points:**
• The content covers fundamental concepts in this area
• This material is from Chapter: {primary_source.chapter_name}
• You can find more details in the uploaded course materials

Would you like me to explain any specific part in more detail? I can help you understand these concepts better using your course materials."""

        return response
    
    def _calculate_confidence(self, search_results: List[SearchResult], user_message: str) -> float:
        """Calculate confidence score based on search results quality"""
        if not search_results:
            return 0.1
        
        # Simple confidence calculation based on:
        # 1. Number of results found
        # 2. Average similarity scores
        # 3. Content length of results
        
        num_results = len(search_results)
        avg_score = sum(1.0 / (1.0 + result.score) for result in search_results) / num_results
        content_quality = min(sum(len(result.content) for result in search_results) / 1000.0, 1.0)
        
        confidence = (avg_score * 0.4) + (content_quality * 0.3) + (min(num_results / 3.0, 1.0) * 0.3)
        return min(confidence, 0.95)  # Cap at 95%
    
    async def _update_chat_session(
        self, 
        session_id: str, 
        student_id: int, 
        course_id: Optional[int],
        user_message: str,
        ai_response: str
    ):
        """Update or create chat session with new messages"""
        now = datetime.now()
        
        if session_id not in self.active_sessions:
            # Create new session
            self.active_sessions[session_id] = ChatSession(
                session_id=session_id,
                student_id=student_id,
                course_id=course_id,
                messages=[],
                created_at=now,
                updated_at=now
            )
        
        session = self.active_sessions[session_id]
        
        # Add user message
        user_msg = ChatMessage(
            message_id=f"{session_id}_{len(session.messages)}",
            content=user_message,
            role="user",
            timestamp=now
        )
        session.messages.append(user_msg)
        
        # Add AI response
        ai_msg = ChatMessage(
            message_id=f"{session_id}_{len(session.messages)}",
            content=ai_response,
            role="assistant",
            timestamp=now
        )
        session.messages.append(ai_msg)
        
        session.updated_at = now
    
    async def get_chat_history(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session history"""
        return self.active_sessions.get(session_id)
    
    async def start_new_session(self, student_id: int, course_id: Optional[int] = None) -> str:
        """Start a new chat session"""
        from uuid import uuid4
        session_id = str(uuid4())
        
        now = datetime.now()
        self.active_sessions[session_id] = ChatSession(
            session_id=session_id,
            student_id=student_id,
            course_id=course_id,
            messages=[],
            created_at=now,
            updated_at=now
        )
        
        return session_id
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation for analytics"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {}
        
        user_messages = [msg for msg in session.messages if msg.role == "user"]
        ai_messages = [msg for msg in session.messages if msg.role == "assistant"]
        
        return {
            'session_id': session_id,
            'student_id': session.student_id,
            'course_id': session.course_id,
            'total_messages': len(session.messages),
            'user_messages': len(user_messages),
            'ai_responses': len(ai_messages),
            'session_duration': (session.updated_at - session.created_at).total_seconds(),
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }
    
    async def get_popular_topics(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get analytics on popular topics/questions"""
        # In a real implementation, this would analyze message patterns
        # For now, return mock data
        
        return [
            {'topic': 'Data Structures', 'frequency': 25, 'avg_satisfaction': 4.2},
            {'topic': 'Algorithms', 'frequency': 18, 'avg_satisfaction': 4.0},
            {'topic': 'Object-Oriented Programming', 'frequency': 15, 'avg_satisfaction': 4.5},
            {'topic': 'Database Design', 'frequency': 12, 'avg_satisfaction': 3.8},
            {'topic': 'Web Development', 'frequency': 10, 'avg_satisfaction': 4.1}
        ]

# Global instance
chatbot_service = ChatbotService()
