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
import StudentDashboard from './pages/StudentDashboard';
import StudentPerformanceAnalytics from './pages/StudentPerformanceAnalytics';
import MCQTestComponent from './components/MCQTestComponent';

// LearnAid Theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
      light: '#98a9f5',
      dark: '#4c63d2',
    },
    secondary: {
      main: '#764ba2',
      light: '#9575cd',
      dark: '#512da8',
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
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Faculty Routes */}
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
              <Route path="/test/:assignmentId" element={<MCQTestComponent assignmentId={1} onComplete={() => window.location.href = '/student-dashboard'} />} />
              
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
