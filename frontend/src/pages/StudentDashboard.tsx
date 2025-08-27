import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  Avatar,
  Tabs,
  Tab,
  Badge,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  TrendingUp,
  TrendingDown,
  Timer,
  PlayArrow,
  Visibility,
  Star,
  EmojiEvents,
  LocalFireDepartment,
  CheckCircle,
  Warning,
} from '@mui/icons-material';

interface StudentInfo {
  student_id: number;
  name: string;
  student_reg_no: string;
  class: string;
  semester: number;
  department: string;
  cgpa: string;
  total_points: number;
  current_streak: number;
}

interface CourseInfo {
  course_id: number;
  course_name: string;
  course_code: string;
  faculty_name: string;
  semester: number;
  credits: number;
  total_chapters: number;
  current_chapter: number;
  completion_percentage: number;
}

interface ExamResult {
  exam_id: number;
  exam_title: string;
  course_name: string;
  exam_type: string;
  marks_obtained: number;
  total_marks: number;
  percentage: number;
  grade: string;
  exam_date: string;
}

interface PendingTask {
  assignment_id: number;
  task_id: number;
  task_title: string;
  course_name: string;
  chapter_title: string;
  task_type: string;
  difficulty: string;
  time_limit: number;
  due_date: string;
  assignment_reason: string;
  priority: string;
}

interface DashboardData {
  student_info: StudentInfo;
  academic_summary: {
    enrolled_courses: number;
    total_chapters: number;
    completed_chapters: number;
    overall_completion: number;
    average_performance: number;
    weak_chapters_count: number;
  };
  courses: CourseInfo[];
  recent_exam_results: ExamResult[];
  pending_tasks: PendingTask[];
  performance_summary: {
    total_tasks_assigned: number;
    total_tasks_completed: number;
    completion_rate: number;
    weak_chapters: number;
    improvement_needed: boolean;
  };
}

const StudentDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [currentTab, setCurrentTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Mock student ID - in real app, get from authentication context
  // const studentId = 1;

  // Mock dashboard data for development
  const mockDashboardData: DashboardData = {
    student_info: {
      student_id: 1,
      name: 'Alice Johnson',
      student_reg_no: 'CS21B001',
      class: 'IV CSE A',
      semester: 7,
      department: 'Computer Science Engineering',
      cgpa: '8.45',
      total_points: 1250,
      current_streak: 5,
    },
    academic_summary: {
      enrolled_courses: 6,
      total_chapters: 45,
      completed_chapters: 32,
      overall_completion: 71.1,
      average_performance: 67.3,
      weak_chapters_count: 4,
    },
    courses: [
      {
        course_id: 1,
        course_name: 'Data Structures and Algorithms',
        course_code: 'CS301',
        faculty_name: 'Dr. John Smith',
        semester: 7,
        credits: 4,
        total_chapters: 8,
        current_chapter: 6,
        completion_percentage: 75.0,
      },
      {
        course_id: 2,
        course_name: 'Database Management Systems',
        course_code: 'CS302',
        faculty_name: 'Dr. Sarah Wilson',
        semester: 7,
        credits: 3,
        total_chapters: 7,
        current_chapter: 5,
        completion_percentage: 71.4,
      },
    ],
    recent_exam_results: [
      {
        exam_id: 1,
        exam_title: 'CIA 1 - Data Structures',
        course_name: 'Data Structures and Algorithms',
        exam_type: 'cia1',
        marks_obtained: 35.5,
        total_marks: 50,
        percentage: 71.0,
        grade: 'B+',
        exam_date: '2024-01-15',
      },
      {
        exam_id: 2,
        exam_title: 'CIA 1 - Database Systems',
        course_name: 'Database Management Systems',
        exam_type: 'cia1',
        marks_obtained: 42.0,
        total_marks: 50,
        percentage: 84.0,
        grade: 'A',
        exam_date: '2024-01-12',
      },
    ],
    pending_tasks: [
      {
        assignment_id: 1,
        task_id: 1,
        task_title: 'Arrays and Linked Lists Practice',
        course_name: 'Data Structures and Algorithms',
        chapter_title: 'Arrays and Linked Lists',
        task_type: 'frequent_assessment',
        difficulty: 'medium',
        time_limit: 20,
        due_date: '2024-01-25T18:00:00',
        assignment_reason: 'Poor CIA1 performance in Chapter 1 (35%)',
        priority: 'high',
      },
      {
        assignment_id: 2,
        task_id: 2,
        task_title: 'SQL Query Optimization',
        course_name: 'Database Management Systems',
        chapter_title: 'Query Processing',
        task_type: 'remedial',
        difficulty: 'hard',
        time_limit: 30,
        due_date: '2024-01-27T20:00:00',
        assignment_reason: 'Below average performance in optimization concepts',
        priority: 'medium',
      },
    ],
    performance_summary: {
      total_tasks_assigned: 8,
      total_tasks_completed: 5,
      completion_rate: 62.5,
      weak_chapters: 4,
      improvement_needed: true,
    },
  };

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setDashboardData(mockDashboardData);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const startTask = async (taskId: number) => {
    try {
      alert(`Starting task ${taskId}. This will navigate to the MCQ test component!`);
      // Navigate to task attempt page
    } catch (error) {
      console.error('Error starting task:', error);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const getGradeColor = (grade: string): 'success' | 'primary' | 'warning' | 'error' | 'default' => {
    const gradeColors: { [key: string]: 'success' | 'primary' | 'warning' | 'error' | 'default' } = {
      'A+': 'success',
      'A': 'success', 
      'B+': 'primary',
      'B': 'primary',
      'C+': 'warning',
      'C': 'warning',
      'D': 'error',
      'F': 'error',
    };
    return gradeColors[grade] || 'default';
  };

  const getPriorityColor = (priority: string): 'error' | 'warning' | 'info' | 'default' => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getPerformanceIcon = (percentage: number) => {
    if (percentage >= 80) return <TrendingUp color="success" />;
    if (percentage >= 60) return <TrendingUp color="warning" />;
    return <TrendingDown color="error" />;
  };

  if (loading && !dashboardData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!dashboardData) return null;

  return (
    <Box sx={{ maxWidth: '100%', mx: 'auto' }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
          <Avatar
            sx={{
              width: 60,
              height: 60,
              bgcolor: 'primary.main',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}
          >
            {dashboardData.student_info.name.split(' ').map(n => n[0]).join('')}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 0.5 }}>
              Welcome back, {dashboardData.student_info.name.split(' ')[0]}! 👋
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
              <Typography variant="body1" color="text.secondary">
                {dashboardData.student_info.student_reg_no} • {dashboardData.student_info.class}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocalFireDepartment color="warning" />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {dashboardData.student_info.current_streak} day streak
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <EmojiEvents color="primary" />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {dashboardData.student_info.total_points} points
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Quick Stats Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr 1fr' },
        gap: 3,
        mb: 4 
      }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: 2, 
                backgroundColor: 'primary.light',
                color: 'primary.contrastText'
              }}>
                <SchoolIcon />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  {dashboardData.academic_summary.enrolled_courses}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Courses
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: 2, 
                backgroundColor: 'success.light',
                color: 'success.contrastText'
              }}>
                <CheckCircle />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                  {dashboardData.academic_summary.overall_completion.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Course Progress
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: 2, 
                backgroundColor: dashboardData.pending_tasks.length > 0 ? 'warning.light' : 'success.light',
                color: dashboardData.pending_tasks.length > 0 ? 'warning.contrastText' : 'success.contrastText'
              }}>
                <AssignmentIcon />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ 
                  fontWeight: 600, 
                  color: dashboardData.pending_tasks.length > 0 ? 'warning.main' : 'success.main' 
                }}>
                  {dashboardData.pending_tasks.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Tasks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: 2, 
                backgroundColor: dashboardData.academic_summary.weak_chapters_count > 0 ? 'error.light' : 'success.light',
                color: dashboardData.academic_summary.weak_chapters_count > 0 ? 'error.contrastText' : 'success.contrastText'
              }}>
                {dashboardData.academic_summary.weak_chapters_count > 0 ? <Warning /> : <Star />}
              </Box>
              <Box>
                <Typography variant="h4" sx={{ 
                  fontWeight: 600, 
                  color: dashboardData.academic_summary.weak_chapters_count > 0 ? 'error.main' : 'success.main'
                }}>
                  {dashboardData.academic_summary.weak_chapters_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dashboardData.academic_summary.weak_chapters_count > 0 ? 'Weak Areas' : 'All Strong!'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Main Content Tabs */}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab 
                label={
                  <Badge badgeContent={dashboardData.pending_tasks.length} color="error" invisible={dashboardData.pending_tasks.length === 0}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AssignmentIcon fontSize="small" />
                      Pending Tasks
                    </Box>
                  </Badge>
                } 
              />
              <Tab label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SchoolIcon fontSize="small" />
                  My Courses
                </Box>
              } />
              <Tab label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DashboardIcon fontSize="small" />
                  Recent Results
                </Box>
              } />
            </Tabs>
          </Box>

          {/* Pending Tasks Tab */}
          {currentTab === 0 && (
            <Box>
              {dashboardData.pending_tasks.length === 0 ? (
                <Alert severity="success" icon={<CheckCircle />}>
                  🎉 Great job! You have no pending tasks. Keep up the excellent work!
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Task Details</TableCell>
                        <TableCell>Course & Chapter</TableCell>
                        <TableCell>Priority</TableCell>
                        <TableCell>Duration</TableCell>
                        <TableCell>Due Date</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.pending_tasks.map((task) => (
                        <TableRow key={task.assignment_id}>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                                {task.task_title}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {task.assignment_reason}
                              </Typography>
                              <Box sx={{ mt: 0.5 }}>
                                <Chip
                                  label={task.task_type.replace('_', ' ')}
                                  size="small"
                                  variant="outlined"
                                  color="primary"
                                />
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {task.course_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {task.chapter_title}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={task.priority.toUpperCase()}
                              size="small"
                              color={getPriorityColor(task.priority)}
                              variant={task.priority === 'high' ? 'filled' : 'outlined'}
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Timer fontSize="small" color="action" />
                              <Typography variant="body2">
                                {task.time_limit} min
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="error" sx={{ fontWeight: 500 }}>
                              {new Date(task.due_date).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(task.due_date).toLocaleTimeString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="contained"
                              size="small"
                              startIcon={<PlayArrow />}
                              onClick={() => startTask(task.task_id)}
                              color={task.priority === 'high' ? 'error' : 'primary'}
                            >
                              Start Task
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {/* My Courses Tab */}
          {currentTab === 1 && (
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              gap: 3 
            }}>
              {dashboardData.courses.map((course) => (
                <Card key={course.course_id} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                          {course.course_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {course.course_code} • {course.credits} Credits
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Faculty: {course.faculty_name}
                        </Typography>
                      </Box>
                      <Chip
                        label={`Sem ${course.semester}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Progress: Chapter {course.current_chapter} of {course.total_chapters}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {course.completion_percentage.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={course.completion_percentage}
                        color={course.completion_percentage > 75 ? 'success' : course.completion_percentage > 50 ? 'primary' : 'warning'}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Visibility />}
                      fullWidth
                    >
                      View Course Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}

          {/* Recent Results Tab */}
          {currentTab === 2 && (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Exam</TableCell>
                    <TableCell>Course</TableCell>
                    <TableCell>Performance</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Trend</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData.recent_exam_results.map((result) => (
                    <TableRow key={result.exam_id}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {result.exam_title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {result.exam_type.toUpperCase()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {result.course_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {result.marks_obtained}/{result.total_marks}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            ({result.percentage.toFixed(1)}%)
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={result.percentage}
                          color={result.percentage > 80 ? 'success' : result.percentage > 60 ? 'primary' : 'warning'}
                          sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.grade}
                          size="small"
                          color={getGradeColor(result.grade)}
                          variant="filled"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(result.exam_date).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title={`Performance: ${result.percentage.toFixed(1)}%`}>
                          <IconButton size="small">
                            {getPerformanceIcon(result.percentage)}
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default StudentDashboard;
