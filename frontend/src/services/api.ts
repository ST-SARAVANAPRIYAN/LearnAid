import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth Service
export const authService = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { username: email, password }),
  
  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),
  
  getFacultyProfile: () =>
    api.get('/api/v1/faculty/profile'),
};

// Faculty Service
export const facultyService = {
  // Dashboard
  getDashboard: () =>
    api.get('/api/v1/faculty/dashboard'),
  
  // Courses
  getCourses: () =>
    api.get('/api/v1/faculty/courses'),
  
  createCourse: (courseData: any) =>
    api.post('/api/v1/faculty/courses', courseData),
  
  updateCourse: (courseId: number, courseData: any) =>
    api.put(`/api/v1/faculty/courses/${courseId}`, courseData),
  
  deleteCourse: (courseId: number) =>
    api.delete(`/api/v1/faculty/courses/${courseId}`),
  
  getCourse: (courseId: number) =>
    api.get(`/api/v1/faculty/courses/${courseId}`),
  
  // Chapters
  getChapters: (courseId: number) =>
    api.get(`/api/v1/faculty/courses/${courseId}/chapters`),
  
  createChapter: (courseId: number, chapterData: any) =>
    api.post(`/api/v1/faculty/courses/${courseId}/chapters`, chapterData),
  
  updateChapter: (courseId: number, chapterId: number, chapterData: any) =>
    api.put(`/api/v1/faculty/courses/${courseId}/chapters/${chapterId}`, chapterData),
  
  deleteChapter: (courseId: number, chapterId: number) =>
    api.delete(`/api/v1/faculty/courses/${courseId}/chapters/${chapterId}`),
  
  uploadChapterPDF: (courseId: number, chapterId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/v1/faculty/courses/${courseId}/chapters/${chapterId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Exams
  getExams: () =>
    api.get('/api/v1/faculty/exams'),
  
  createExam: (examData: any) =>
    api.post('/api/v1/faculty/exams', examData),
  
  updateExam: (examId: number, examData: any) =>
    api.put(`/api/v1/faculty/exams/${examId}`, examData),
  
  deleteExam: (examId: number) =>
    api.delete(`/api/v1/faculty/exams/${examId}`),
  
  getExam: (examId: number) =>
    api.get(`/api/v1/faculty/exams/${examId}`),

  // Questions
  getExamQuestions: (examId: number) =>
    api.get(`/api/v1/faculty/exams/${examId}/questions`),
  
  createQuestion: (questionData: any) =>
    api.post(`/api/v1/faculty/exams/${questionData.exam_id}/questions`, questionData),
  
  updateQuestion: (questionId: number, questionData: any) =>
    api.put(`/api/v1/faculty/questions/${questionId}`, questionData),
  
  deleteQuestion: (questionId: number) =>
    api.delete(`/api/v1/faculty/questions/${questionId}`),
  
  // Students
  getStudents: (courseId?: number) => {
    const url = courseId 
      ? `/api/v1/faculty/students?course_id=${courseId}`
      : '/api/v1/faculty/students';
    return api.get(url);
  },
  
  getStudentPerformance: (courseId: number, studentId?: number) => {
    const url = studentId
      ? `/api/v1/faculty/courses/${courseId}/students/${studentId}/performance`
      : `/api/v1/faculty/courses/${courseId}/students/performance`;
    return api.get(url);
  },
  
  bulkCreateStudentResponses: (responseData: any) =>
    api.post('/api/v1/faculty/student-responses/bulk', responseData),
};

export default api;
