"""
LLM Service for task generation and content processing using Groq API
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option (0-3)
    explanation: str
    difficulty: str  # "easy", "medium", "hard"
    chapter_topic: str

class GroqLLMService:
    """Service for interacting with Groq API for educational content generation"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client with API key"""
        try:
            # For now using a placeholder - in production this would be from environment
            api_key = os.getenv("GROQ_API_KEY", "gsk_placeholder_key")
            if api_key == "gsk_placeholder_key":
                logger.warning("Using placeholder Groq API key - set GROQ_API_KEY environment variable")
            
            self.client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None
    
    async def generate_mcq_from_content(
        self, 
        content: str, 
        topic: str, 
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> List[MCQQuestion]:
        """
        Generate MCQ questions from given content
        
        Args:
            content: Text content to generate questions from
            topic: Topic/chapter name for context
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of MCQQuestion objects
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return self._generate_mock_questions(topic, num_questions, difficulty)
        
        try:
            prompt = self._create_mcq_prompt(content, topic, num_questions, difficulty)
            
            # For now, return mock data since we need actual Groq API key
            # In production, this would call the actual API
            logger.info(f"Generating {num_questions} MCQ questions for topic: {topic}")
            return self._generate_mock_questions(topic, num_questions, difficulty)
            
        except Exception as e:
            logger.error(f"Error generating MCQ questions: {e}")
            return self._generate_mock_questions(topic, num_questions, difficulty)
    
    def _create_mcq_prompt(self, content: str, topic: str, num_questions: int, difficulty: str) -> str:
        """Create a well-structured prompt for MCQ generation"""
        return f"""
        You are an expert educator creating multiple-choice questions for students.
        
        Topic: {topic}
        Difficulty Level: {difficulty}
        Content: {content[:2000]}...
        
        Generate {num_questions} multiple-choice questions based on the above content.
        Each question should:
        1. Be clear and unambiguous
        2. Have 4 options (A, B, C, D)
        3. Have exactly one correct answer
        4. Include a brief explanation for the correct answer
        5. Be at {difficulty} difficulty level
        
        Format your response as valid JSON:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Explanation for correct answer",
                    "difficulty": "{difficulty}",
                    "chapter_topic": "{topic}"
                }}
            ]
        }}
        """
    
    def _generate_mock_questions(self, topic: str, num_questions: int, difficulty: str) -> List[MCQQuestion]:
        """Generate mock MCQ questions for development/testing"""
        mock_questions = []
        
        question_templates = [
            {
                "question": f"What is the primary concept discussed in {topic}?",
                "options": [
                    f"Basic principles of {topic}",
                    f"Advanced applications of {topic}",
                    f"Historical background of {topic}",
                    f"Future trends in {topic}"
                ],
                "correct_answer": 0,
                "explanation": f"The primary concept focuses on understanding the basic principles of {topic}."
            },
            {
                "question": f"Which of the following best describes {topic}?",
                "options": [
                    "A theoretical framework",
                    "A practical application",
                    "A comprehensive methodology",
                    "An experimental approach"
                ],
                "correct_answer": 2,
                "explanation": f"{topic} is best described as a comprehensive methodology that encompasses both theory and practice."
            },
            {
                "question": f"What are the key benefits of understanding {topic}?",
                "options": [
                    "Improved problem-solving skills",
                    "Better analytical thinking",
                    "Enhanced practical knowledge",
                    "All of the above"
                ],
                "correct_answer": 3,
                "explanation": f"Understanding {topic} provides multiple benefits including improved problem-solving, analytical thinking, and practical knowledge."
            },
            {
                "question": f"How does {topic} relate to real-world applications?",
                "options": [
                    "It has limited practical use",
                    "It provides theoretical foundation only",
                    "It offers direct practical applications",
                    "It requires further research"
                ],
                "correct_answer": 2,
                "explanation": f"{topic} offers direct practical applications that can be implemented in real-world scenarios."
            },
            {
                "question": f"What is the most important aspect to remember about {topic}?",
                "options": [
                    "Its historical significance",
                    "Its core principles and concepts",
                    "Its future potential",
                    "Its complexity level"
                ],
                "correct_answer": 1,
                "explanation": f"The most important aspect is understanding the core principles and concepts of {topic}."
            }
        ]
        
        for i in range(min(num_questions, len(question_templates))):
            template = question_templates[i]
            mock_questions.append(MCQQuestion(
                question=template["question"],
                options=template["options"],
                correct_answer=template["correct_answer"],
                explanation=template["explanation"],
                difficulty=difficulty,
                chapter_topic=topic
            ))
        
        # If more questions needed, cycle through templates with variations
        while len(mock_questions) < num_questions:
            base_idx = len(mock_questions) % len(question_templates)
            template = question_templates[base_idx]
            
            mock_questions.append(MCQQuestion(
                question=f"(Extended) {template['question']}",
                options=template["options"],
                correct_answer=template["correct_answer"],
                explanation=template["explanation"],
                difficulty=difficulty,
                chapter_topic=topic
            ))
        
        logger.info(f"Generated {len(mock_questions)} mock questions for {topic}")
        return mock_questions
    
    async def generate_task_description(self, weak_chapters: List[str], student_performance: Dict) -> str:
        """Generate a personalized task description based on student performance"""
        if not weak_chapters:
            return "Complete the assigned reading and practice exercises to strengthen your understanding."
        
        weak_areas = ", ".join(weak_chapters[:3])  # Limit to top 3 weak areas
        
        return f"""
        Based on your recent performance analysis, you need additional practice in: {weak_areas}.
        
        This personalized task includes:
        • Targeted questions focusing on your weak areas
        • Step-by-step explanations for better understanding
        • Practice exercises to reinforce key concepts
        
        Take your time to work through each question carefully and review the explanations to improve your grasp of these topics.
        """
    
    async def validate_question_quality(self, question: MCQQuestion) -> Dict[str, Any]:
        """Validate the quality of generated questions"""
        validation_result = {
            "is_valid": True,
            "quality_score": 0.85,  # Mock score
            "issues": [],
            "suggestions": []
        }
        
        # Basic validation checks
        if len(question.question.strip()) < 10:
            validation_result["issues"].append("Question too short")
            validation_result["quality_score"] -= 0.2
        
        if len(question.options) != 4:
            validation_result["issues"].append("Must have exactly 4 options")
            validation_result["quality_score"] -= 0.3
        
        if question.correct_answer < 0 or question.correct_answer >= len(question.options):
            validation_result["issues"].append("Invalid correct answer index")
            validation_result["quality_score"] -= 0.4
        
        if len(question.explanation.strip()) < 20:
            validation_result["issues"].append("Explanation too brief")
            validation_result["quality_score"] -= 0.1
        
        validation_result["is_valid"] = validation_result["quality_score"] >= 0.6
        
        return validation_result

# Global instance
llm_service = GroqLLMService()
