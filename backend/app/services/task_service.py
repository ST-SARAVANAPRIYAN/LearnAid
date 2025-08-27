"""
Task Generation Service for intelligent task assignment and performance analysis
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.user import Student
from app.models.course import Course, Chapter
from app.models.exam import ExamResult, ExamResponse
from app.models.task import Task, TaskQuestion, TaskAssignment
from app.services.llm_service import llm_service, MCQQuestion
from app.services.pdf_service import pdf_service

logger = logging.getLogger(__name__)

class TaskGenerationService:
    """Service for intelligent task generation based on student performance"""
    
    def __init__(self):
        self.performance_threshold = 0.6  # 60% threshold for identifying weak areas
        self.min_questions_per_task = 5
        self.max_questions_per_task = 15
        
    async def analyze_student_performance(self, db: Session, student_id: int) -> Dict[str, Any]:
        """
        Analyze student's performance to identify weak chapters
        
        Args:
            db: Database session
            student_id: Student ID to analyze
            
        Returns:
            Dict containing performance analysis data
        """
        try:
            # Get student's exam results with chapter breakdown
            exam_results = db.query(ExamResult).filter(
                ExamResult.student_id == student_id
            ).all()
            
            if not exam_results:
                logger.info(f"No exam results found for student {student_id}")
                return {
                    "student_id": student_id,
                    "weak_chapters": [],
                    "strong_chapters": [],
                    "overall_performance": 0.0,
                    "recommendation": "Complete more assessments to get personalized recommendations"
                }
            
            # Analyze chapter-wise performance
            chapter_performance = {}
            total_score = 0
            total_exams = 0
            
            for result in exam_results:
                # Get exam responses to analyze chapter-wise performance
                responses = db.query(ExamResponse).filter(
                    ExamResponse.exam_result_id == result.id
                ).all()
                
                # Calculate chapter performance from responses
                chapter_scores = self._calculate_chapter_performance(db, responses)
                
                for chapter_id, score in chapter_scores.items():
                    if chapter_id not in chapter_performance:
                        chapter_performance[chapter_id] = []
                    chapter_performance[chapter_id].append(score)
                
                total_score += result.score
                total_exams += 1
            
            # Calculate average performance per chapter
            chapter_averages = {}
            for chapter_id, scores in chapter_performance.items():
                chapter_averages[chapter_id] = sum(scores) / len(scores)
            
            # Identify weak and strong chapters
            weak_chapters = []
            strong_chapters = []
            
            for chapter_id, avg_score in chapter_averages.items():
                chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                chapter_name = chapter.name if chapter else f"Chapter {chapter_id}"
                
                if avg_score < self.performance_threshold:
                    weak_chapters.append({
                        "chapter_id": chapter_id,
                        "chapter_name": chapter_name,
                        "performance": avg_score,
                        "needs_improvement": True
                    })
                else:
                    strong_chapters.append({
                        "chapter_id": chapter_id,
                        "chapter_name": chapter_name,
                        "performance": avg_score,
                        "needs_improvement": False
                    })
            
            # Sort by performance (weakest first for weak chapters)
            weak_chapters.sort(key=lambda x: x["performance"])
            strong_chapters.sort(key=lambda x: x["performance"], reverse=True)
            
            overall_performance = total_score / total_exams if total_exams > 0 else 0.0
            
            analysis = {
                "student_id": student_id,
                "weak_chapters": weak_chapters[:5],  # Top 5 weak areas
                "strong_chapters": strong_chapters[:3],  # Top 3 strong areas
                "overall_performance": round(overall_performance, 2),
                "total_exams_taken": total_exams,
                "recommendation": self._generate_recommendation(weak_chapters, overall_performance)
            }
            
            logger.info(f"Performance analysis completed for student {student_id}: {len(weak_chapters)} weak chapters identified")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing student performance for {student_id}: {e}")
            return {
                "student_id": student_id,
                "weak_chapters": [],
                "strong_chapters": [],
                "overall_performance": 0.0,
                "recommendation": "Unable to analyze performance at this time"
            }
    
    def _calculate_chapter_performance(self, db: Session, responses: List[ExamResponse]) -> Dict[int, float]:
        """Calculate performance per chapter from exam responses"""
        chapter_scores = {}
        
        for response in responses:
            if response.question and response.question.chapter_id:
                chapter_id = response.question.chapter_id
                is_correct = response.selected_option == response.question.correct_option
                
                if chapter_id not in chapter_scores:
                    chapter_scores[chapter_id] = {"correct": 0, "total": 0}
                
                chapter_scores[chapter_id]["total"] += 1
                if is_correct:
                    chapter_scores[chapter_id]["correct"] += 1
        
        # Convert to percentage scores
        chapter_averages = {}
        for chapter_id, scores in chapter_scores.items():
            if scores["total"] > 0:
                chapter_averages[chapter_id] = scores["correct"] / scores["total"]
        
        return chapter_averages
    
    def _generate_recommendation(self, weak_chapters: List[Dict], overall_performance: float) -> str:
        """Generate personalized recommendation based on performance"""
        if not weak_chapters:
            if overall_performance >= 0.85:
                return "Excellent performance! Consider exploring advanced topics or helping peers."
            else:
                return "Good performance overall. Keep up the consistent effort!"
        
        weak_count = len(weak_chapters)
        if weak_count == 1:
            return f"Focus on improving {weak_chapters[0]['chapter_name']} with additional practice."
        elif weak_count <= 3:
            chapter_names = ", ".join([ch["chapter_name"] for ch in weak_chapters[:2]])
            return f"Concentrate on {chapter_names} and similar topics for better performance."
        else:
            return f"Multiple areas need attention. Start with {weak_chapters[0]['chapter_name']} and work systematically."
    
    async def generate_personalized_task(
        self, 
        db: Session, 
        student_id: int,
        course_id: int,
        task_type: str = "improvement"
    ) -> Optional[int]:
        """
        Generate a personalized task for a student based on their performance
        
        Args:
            db: Database session
            student_id: Student ID
            course_id: Course ID for the task
            task_type: Type of task ("improvement", "reinforcement", "challenge")
            
        Returns:
            Task ID if successful, None otherwise
        """
        try:
            # Analyze student performance
            performance_analysis = await self.analyze_student_performance(db, student_id)
            
            if task_type == "improvement" and performance_analysis["weak_chapters"]:
                # Focus on weak areas
                target_chapters = performance_analysis["weak_chapters"][:3]
                difficulty = "medium"
                num_questions = min(self.max_questions_per_task, max(self.min_questions_per_task, len(target_chapters) * 3))
            elif task_type == "reinforcement" and performance_analysis["strong_chapters"]:
                # Reinforce strong areas
                target_chapters = performance_analysis["strong_chapters"][:2]
                difficulty = "medium"
                num_questions = self.min_questions_per_task
            else:
                # General practice task
                target_chapters = performance_analysis["weak_chapters"][:2] if performance_analysis["weak_chapters"] else []
                if not target_chapters:
                    # Get random chapters from the course
                    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).limit(2).all()
                    target_chapters = [{"chapter_id": ch.id, "chapter_name": ch.name} for ch in chapters]
                difficulty = "easy"
                num_questions = self.min_questions_per_task
            
            if not target_chapters:
                logger.warning(f"No target chapters found for student {student_id} in course {course_id}")
                return None
            
            # Create task
            task_title = self._generate_task_title(task_type, target_chapters)
            task_description = await llm_service.generate_task_description(
                [ch["chapter_name"] for ch in target_chapters],
                performance_analysis
            )
            
            # Create Task record
            task = Task(
                title=task_title,
                description=task_description,
                course_id=course_id,
                created_by=1,  # System-generated tasks
                task_type=task_type,
                difficulty_level=difficulty,
                total_questions=num_questions,
                time_limit_minutes=num_questions * 2,  # 2 minutes per question
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(task)
            db.flush()  # Get task ID
            
            # Generate questions for each target chapter
            questions_created = 0
            for chapter_info in target_chapters:
                chapter_id = chapter_info["chapter_id"]
                chapter_name = chapter_info["chapter_name"]
                
                # Get chapter content (mock for now)
                chapter_content = await self._get_chapter_content(db, chapter_id)
                
                # Generate questions using LLM
                questions_per_chapter = max(1, num_questions // len(target_chapters))
                mcq_questions = await llm_service.generate_mcq_from_content(
                    chapter_content, 
                    chapter_name, 
                    questions_per_chapter, 
                    difficulty
                )
                
                # Create TaskQuestion records
                for i, mcq in enumerate(mcq_questions):
                    if questions_created >= num_questions:
                        break
                    
                    task_question = TaskQuestion(
                        task_id=task.id,
                        question_text=mcq.question,
                        option_a=mcq.options[0],
                        option_b=mcq.options[1],
                        option_c=mcq.options[2],
                        option_d=mcq.options[3],
                        correct_option=mcq.correct_answer,
                        explanation=mcq.explanation,
                        chapter_id=chapter_id,
                        difficulty_level=mcq.difficulty,
                        question_order=questions_created + 1
                    )
                    
                    db.add(task_question)
                    questions_created += 1
            
            # Update task with actual question count
            task.total_questions = questions_created
            
            # Assign task to student
            assignment = TaskAssignment(
                task_id=task.id,
                student_id=student_id,
                assigned_by=1,  # System assignment
                assigned_at=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=7),  # 1 week deadline
                status="assigned"
            )
            
            db.add(assignment)
            db.commit()
            
            logger.info(f"Generated personalized {task_type} task {task.id} for student {student_id} with {questions_created} questions")
            return task.id
            
        except Exception as e:
            logger.error(f"Error generating personalized task for student {student_id}: {e}")
            db.rollback()
            return None
    
    def _generate_task_title(self, task_type: str, target_chapters: List[Dict]) -> str:
        """Generate an appropriate title for the task"""
        chapter_names = [ch["chapter_name"] for ch in target_chapters[:2]]
        
        if task_type == "improvement":
            if len(chapter_names) == 1:
                return f"Practice Session: {chapter_names[0]}"
            else:
                return f"Improvement Focus: {', '.join(chapter_names)}"
        elif task_type == "reinforcement":
            return f"Reinforcement Practice: {', '.join(chapter_names)}"
        else:
            return f"General Practice: {', '.join(chapter_names)}"
    
    async def _get_chapter_content(self, db: Session, chapter_id: int) -> str:
        """Get content for a chapter (from uploaded PDFs or default content)"""
        try:
            chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not chapter:
                return f"Content for chapter {chapter_id}"
            
            # If chapter has uploaded PDF, use that content
            if hasattr(chapter, 'pdf_path') and chapter.pdf_path:
                try:
                    pdf_content = await pdf_service.process_pdf(chapter.pdf_path)
                    return pdf_content.content[:3000]  # First 3000 characters
                except Exception as e:
                    logger.warning(f"Could not extract PDF content for chapter {chapter_id}: {e}")
            
            # Use chapter description or generate mock content
            if chapter.description:
                return chapter.description
            else:
                return f"""
                This chapter covers the fundamental concepts and principles of {chapter.name}.
                Students will learn about the key topics, practical applications, and theoretical foundations.
                The material includes important definitions, examples, and case studies that demonstrate
                real-world applications of the concepts discussed.
                """
                
        except Exception as e:
            logger.error(f"Error getting content for chapter {chapter_id}: {e}")
            return f"Educational content for {chapter_id}"
    
    async def schedule_weekly_tasks(self, db: Session) -> Dict[str, Any]:
        """Schedule weekly tasks for all active students"""
        try:
            students = db.query(Student).filter(Student.is_active == True).all()
            results = {
                "total_students": len(students),
                "tasks_generated": 0,
                "errors": []
            }
            
            for student in students:
                try:
                    # Get student's enrolled courses
                    courses = db.query(Course).join(
                        # Assuming enrollment relationship exists
                        Course.id == student.id  # This would be the proper join in real implementation
                    ).all()
                    
                    for course in courses[:1]:  # Limit to 1 course per student per week
                        task_id = await self.generate_personalized_task(
                            db, student.id, course.id, "improvement"
                        )
                        if task_id:
                            results["tasks_generated"] += 1
                        
                except Exception as e:
                    error_msg = f"Failed to generate task for student {student.id}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            logger.info(f"Weekly task scheduling completed: {results['tasks_generated']} tasks generated for {results['total_students']} students")
            return results
            
        except Exception as e:
            logger.error(f"Error in weekly task scheduling: {e}")
            return {"error": str(e)}

# Global instance
task_generator = TaskGenerationService()
