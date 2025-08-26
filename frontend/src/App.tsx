import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import Exams from './pages/Exams';
import Students from './pages/Students';
import Profile from './pages/Profile';
import WelcomePage from './pages/Welcome';
import './index.css';

// Create Material UI theme
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
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Poppins',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  shape: {
    borderRadius: 8,
  },
});

function App() {
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
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/courses" element={<Courses />} />
                      <Route path="/exams" element={<Exams />} />
                      <Route path="/students" element={<Students />} />
                      <Route path="/profile" element={<Profile />} />
                    </Routes>
                  </Layout>
                </PrivateRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
