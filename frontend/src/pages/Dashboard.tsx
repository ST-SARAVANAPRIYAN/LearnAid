import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  School as SchoolIcon,
  Quiz as QuizIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface DashboardStats {
  total_courses: number;
  total_exams: number;
  total_students: number;
  avg_score: number;
}

interface CoursePerformance {
  course_name: string;
  avg_score: number;
  total_students: number;
}

interface ExamTypeDistribution {
  exam_type: string;
  count: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [coursePerformance, setCoursePerformance] = useState<CoursePerformance[]>([]);
  const [examDistribution, setExamDistribution] = useState<ExamTypeDistribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Mock data
  const mockStats: DashboardStats = {
    total_courses: 8,
    total_exams: 24,
    total_students: 234,
    avg_score: 78.5,
  };

  const mockCoursePerformance: CoursePerformance[] = [
    { course_name: 'Machine Learning', avg_score: 82.5, total_students: 45 },
    { course_name: 'Data Structures', avg_score: 76.8, total_students: 67 },
    { course_name: 'Database Systems', avg_score: 84.2, total_students: 52 },
    { course_name: 'Web Development', avg_score: 79.6, total_students: 38 },
    { course_name: 'Algorithms', avg_score: 73.4, total_students: 32 },
  ];

  const mockExamDistribution: ExamTypeDistribution[] = [
    { exam_type: 'CIA 1', count: 8 },
    { exam_type: 'CIA 2', count: 6 },
    { exam_type: 'Final', count: 4 },
    { exam_type: 'Quiz', count: 6 },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStats(mockStats);
      setCoursePerformance(mockCoursePerformance);
      setExamDistribution(mockExamDistribution);
      setLoading(false);
    }, 1000);
  }, []);

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c'];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
          🎯 Faculty Dashboard
        </Typography>
        <Typography variant="h6" sx={{ color: 'text.secondary' }}>
          Welcome back, Dr. Faculty!
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 4 }}>
        <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {stats?.total_courses}
                </Typography>
                <Typography variant="body1">Total Courses</Typography>
              </Box>
              <SchoolIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {stats?.total_students}
                </Typography>
                <Typography variant="body1">Total Students</Typography>
              </Box>
              <PeopleIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {stats?.total_exams}
                </Typography>
                <Typography variant="body1">Total Exams</Typography>
              </Box>
              <QuizIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {stats?.avg_score?.toFixed(1)}%
                </Typography>
                <Typography variant="body1">Average Score</Typography>
              </Box>
              <TrendingUpIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Charts Section */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3, mb: 4 }}>
        {/* Course Performance Chart */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            📊 Course Performance
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={coursePerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="course_name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="avg_score" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>

        {/* Exam Distribution Chart */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            📋 Exam Distribution
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={examDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                label={({ exam_type, count }) => `${exam_type}: ${count}`}
              >
                {examDistribution.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Box>

      {/* Quick Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
          🚀 Quick Actions
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
          <Card sx={{ p: 2, textAlign: 'center', cursor: 'pointer', '&:hover': { bgcolor: 'primary.light', color: 'white' } }}>
            <SchoolIcon sx={{ fontSize: 40, mb: 1, color: 'primary.main' }} />
            <Typography variant="body2">Create New Course</Typography>
          </Card>
          
          <Card sx={{ p: 2, textAlign: 'center', cursor: 'pointer', '&:hover': { bgcolor: 'secondary.light', color: 'white' } }}>
            <QuizIcon sx={{ fontSize: 40, mb: 1, color: 'secondary.main' }} />
            <Typography variant="body2">Create New Exam</Typography>
          </Card>
          
          <Card sx={{ p: 2, textAlign: 'center', cursor: 'pointer', '&:hover': { bgcolor: 'success.light', color: 'white' } }}>
            <PeopleIcon sx={{ fontSize: 40, mb: 1, color: 'success.main' }} />
            <Typography variant="body2">View Students</Typography>
          </Card>
          
          <Card sx={{ p: 2, textAlign: 'center', cursor: 'pointer', '&:hover': { bgcolor: 'info.light', color: 'white' } }}>
            <TrendingUpIcon sx={{ fontSize: 40, mb: 1, color: 'info.main' }} />
            <Typography variant="body2">Performance Analytics</Typography>
          </Card>
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;
