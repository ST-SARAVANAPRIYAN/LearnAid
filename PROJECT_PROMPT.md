# 🚀  LearnAid – Intelligent Learning & Performance Support System

You are GitHub Copilot. Assist me in building this project in **Agile sprints**.  
The project stack is:
- **Frontend:** React (Material UI / Tailwind)
- **Backend:** FastAPI (Python 3.11+)
- **Database:** SQLite (SQLAlchemy ORM)
- **ML/LLM:**  groq api or local llm+ FAISS/ChromaDB for embeddings

---

## 🎯 Core Modules

### 1. Admin Module
- Manage **faculty** (CRUD).
- Manage **students** (CRUD).
- Assign faculty → departments & classes.
- High-level dashboard: courses, faculty, student counts.

### 2. Faculty Module
- **Student Management**:
  - Create, delete, modify students.
  - Group by **class** and **department**.
- **Course Management**:
  - Create courses (name, dept, overview, chapters, topics).
  - Upload **chapter PDFs** (stored for chatbot & task generation).

#### **Exam Management (Offline CIA Assessments)**:
- **Create CIA Exams** (CIA1, CIA2, CIA3, Semester):
  - Define exam structure: total questions, marks distribution, duration.
  - **Question-Chapter Mapping**: Map each question to specific chapters.
  - Example: CIA1 (50 marks total):
    - Q1-3 (2 marks each) → Chapter 1
    - Q4-6 (2 marks each) → Chapter 2  
    - Q7-10 (2 marks each) → Chapter 3
    - Q11 (15 marks) → Chapter 1
    - Q12 (15 marks) → Chapter 2
- **Mark Entry & Performance Calculation**:
  - Enter student marks for **each individual question**.
  - System auto-calculates **chapter-wise performance** based on question mapping.
  - Generate performance reports showing student weaknesses by chapter.

### **Frequent Assessments (Task-based)**
- **Task Assignment System**: 
  - Auto-generate tasks for students who performed poorly in specific chapters from CIA exams
  - MCQ assessment APIs with timed tests
  - Task completion tracking and progress monitoring
  - Individual student task scheduling (daily/bi-daily based on performance gaps)

- **Student Performance Analytics**: Individual student progress tracking with chapter-wise performance breakdown and personalized task assignments
- **Task Management**: Assign targeted tasks to students who performed poorly in specific chapters, with automated scheduling and progress tracking

### 3. Student Module
- View assigned courses, chapters, and exam performance (chapter-wise breakdown).
- Receive and complete **daily/periodic tasks**.
- Attempt MCQ assessments with countdown timers.
- View performance trends over time.
- **Self-learning Mode**:
  - Select course → chapter.
  - Ask chatbot questions about uploaded course PDFs.
  - Get static/dynamic answers (RAG + LLM).
- Gamification: points, badges, streaks.

---

---

## ⚡ Development Sprints

### **Sprint 1 – Backend Setup**
- Initialize FastAPI + SQLite.
- Implement models: `User`, `Student`, `Faculty`, `Course`, `Chapter`, `Exam`, `Question`, `Marks`, `Task`, `Performance`.
- JWT authentication.
- CRUD routes for Admin, Faculty, Student.

### **Sprint 2 – Faculty Dashboard**
- APIs for:
  - Course creation + chapter upload.
  - Exam creation + question mapping.
  - Student marks entry → chapter performance calculation.
- React pages for faculty dashboard with forms + analytics.

### **Sprint 3 – Student Dashboard**
- APIs for:
  - Fetch course/chapter data.
  - Fetch CIA results (chapter breakdown).
  - Task generation + retrieval.
- React student dashboard + MCQ test component + progress charts.

### **Sprint 4 – Task & LLM Integration**
- Implement LLM-based task generator (use HuggingFace/OpenAI + embeddings).
- Generate MCQ from uploaded PDF chapter.
- Store generated tasks in DB.
- Student attempts tasks; store results.

### **Sprint 5 – Chatbot & Self-Learning**
- Upload PDFs → chunk + embed → store in FAISS/Chroma.
- Student chatbot interface:
  - Query embeddings + LLM response.
- React chatbot UI.

### **Sprint 6 – Admin Panel**
- Manage faculty, students, departments.
- Analytics dashboard.

---

## ✅ Copilot Instructions
When generating code, Copilot should:
- Use **clean separation** (routers, models, schemas).
- Generate **SQLAlchemy models** with proper relationships.
- Always add **docstrings + comments**.
- For frontend:
  - Use **Material UI** for styling.
  - Use **React Router** for navigation.
  - Use **Axios** for API calls.
- Provide **sample seed data** for testing (students, faculty, sample exam).
- Add **charts** in analytics (Recharts/Chart.js).
- Include **unit tests** for backend services.

---