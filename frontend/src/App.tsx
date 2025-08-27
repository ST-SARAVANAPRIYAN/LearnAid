import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import Students from './pages/Students';
import Exams from './pages/Exams';
import Tasks from './pages/Tasks';
import Performance from './pages/Performance';
import Analytics from './pages/Analytics';
import TaskGeneration from './pages/TaskGeneration';
import Profile from './pages/Profile';
import WelcomePage from './pages/Welcome';
import StudentDashboard from './pages/StudentDashboard';
import StudentPerformanceAnalytics from './pages/StudentPerformanceAnalytics';
import StudentCourses from './pages/StudentCourses';
import StudentCIAResults from './pages/StudentCIAResults';
import StudentTasks from './pages/StudentTasks';
import MCQTestComponent from './components/MCQTestComponent';
import Login from './pages/Login';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import './index.css';

// LearnAid Theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#4361ee',
      light: '#7b96ff',
      dark: '#1565c0',
    },
    secondary: {
      main: '#ff9f1c',
    },
    success: {
      main: '#06d6a0',
    },
    info: {
      main: '#54c5eb',
    },
    warning: {
      main: '#ffd166',
    },
    error: {
      main: '#ef476f',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#2c3e50',
      secondary: '#7f8c8d',
    },
  },
  typography: {
    fontFamily: [
      'Poppins',
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      'sans-serif',
    ].join(','),
  },
  shape: {
    borderRadius: 12,
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/app/*"
              element={
                <PrivateRoute>
                  <Box sx={{ display: 'flex', minHeight: '100vh' }}>
                    <Layout>
                      <Routes>
                        {/* Faculty Routes */}
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/courses" element={<Courses />} />
                        <Route path="/students" element={<Students />} />
                        <Route path="/exams" element={<Exams />} />
                        <Route path="/tasks" element={<Tasks />} />
                        <Route path="/task-generation" element={<TaskGeneration />} />
                        <Route path="/performance" element={<Performance />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/profile" element={<Profile />} />
                        
                        {/* Student Routes */}
                        <Route path="/student-dashboard" element={<StudentDashboard />} />
                        <Route path="/student-performance" element={<StudentPerformanceAnalytics />} />
                        <Route path="/student/courses" element={<StudentCourses />} />
                        <Route path="/student/cia-results" element={<StudentCIAResults />} />
                        <Route path="/student/tasks" element={<StudentTasks />} />
                        <Route path="/test/:assignmentId" element={<MCQTestComponent assignmentId={1} onComplete={() => window.location.href = '/app/student-dashboard'} />} />
                        
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                      </Routes>
                    </Layout>
                  </Box>
                </PrivateRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
