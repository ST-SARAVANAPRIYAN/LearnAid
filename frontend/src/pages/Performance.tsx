import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  TrendingDown,
  TrendingUp,
  Assignment,
  School,
  Person,
  Analytics,
  Refresh,
  Assignment as TaskIcon,
} from '@mui/icons-material';

interface WeakStudent {
  student_id: number;
  student_name: string;
  student_reg_no: string;
  chapter_id: number;
  chapter_title: string;
  performance_percentage: number;
  performance_level: string;
  tasks_assigned: number;
  tasks_completed: number;
  last_exam_date: string | null;
  needs_task_assignment: boolean;
}

interface PerformanceData {
  course_id: number;
  chapter_id?: number;
  performance_threshold: number;
  weak_students: WeakStudent[];
  total_weak_students: number;
}

const Performance: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [selectedCourse, setSelectedCourse] = useState(1);
  const [selectedChapter, setSelectedChapter] = useState<number | ''>('');
  const [performanceThreshold, setPerformanceThreshold] = useState(50);
  const [error, setError] = useState<string | null>(null);

  // Mock data for development
  const mockCourses = [
    { id: 1, name: 'Data Structures and Algorithms', code: 'CS301' },
    { id: 2, name: 'Database Management Systems', code: 'CS302' },
    { id: 3, name: 'Operating Systems', code: 'CS303' },
  ];

  const mockChapters = [
    { id: 1, title: 'Arrays and Linked Lists', course_id: 1 },
    { id: 2, title: 'Stacks and Queues', course_id: 1 },
    { id: 3, title: 'Trees and Graphs', course_id: 1 },
  ];

  const mockPerformanceData: PerformanceData = {
    course_id: 1,
    chapter_id: selectedChapter || undefined,
    performance_threshold: performanceThreshold,
    weak_students: [
      {
        student_id: 1,
        student_name: 'Alice Johnson',
        student_reg_no: 'CS21B001',
        chapter_id: 1,
        chapter_title: 'Arrays and Linked Lists',
        performance_percentage: 35.5,
        performance_level: 'needs_improvement',
        tasks_assigned: 2,
        tasks_completed: 1,
        last_exam_date: '2024-01-15',
        needs_task_assignment: true,
      },
      {
        student_id: 2,
        student_name: 'Bob Wilson',
        student_reg_no: 'CS21B002',
        chapter_id: 2,
        chapter_title: 'Stacks and Queues',
        performance_percentage: 42.0,
        performance_level: 'needs_improvement',
        tasks_assigned: 1,
        tasks_completed: 0,
        last_exam_date: '2024-01-15',
        needs_task_assignment: true,
      },
      {
        student_id: 3,
        student_name: 'Carol Davis',
        student_reg_no: 'CS21B003',
        chapter_id: 3,
        chapter_title: 'Trees and Graphs',
        performance_percentage: 28.5,
        performance_level: 'poor',
        tasks_assigned: 0,
        tasks_completed: 0,
        last_exam_date: '2024-01-15',
        needs_task_assignment: true,
      },
    ],
    total_weak_students: 3,
  };

  const loadPerformanceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setPerformanceData(mockPerformanceData);
    } catch (err) {
      setError('Failed to load performance data');
      console.error('Error loading performance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoAssignTasks = async () => {
    if (!performanceData) return;
    
    try {
      setLoading(true);
      // Simulate API call for auto-assignment
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Refresh data after assignment
      await loadPerformanceData();
      
      // Show success message (in real app, use snackbar)
      alert('Tasks auto-assigned successfully!');
    } catch (err) {
      setError('Failed to auto-assign tasks');
      console.error('Error auto-assigning tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPerformanceData();
  }, [selectedCourse, selectedChapter, performanceThreshold]);

  const getPerformanceLevelColor = (level: string) => {
    switch (level) {
      case 'excellent': return 'success';
      case 'good': return 'primary';
      case 'average': return 'warning';
      case 'needs_improvement': return 'error';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const getPerformanceLevelIcon = (percentage: number) => {
    if (percentage < 40) return <TrendingDown color="error" />;
    if (percentage < 60) return <TrendingUp color="warning" />;
    return <TrendingUp color="success" />;
  };

  if (loading && !performanceData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '100%', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 2 }}>
          📊 Student Performance Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Identify students struggling with specific chapters and assign targeted improvement tasks
        </Typography>
      </Box>

      {/* Filter Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Course</InputLabel>
              <Select
                value={selectedCourse}
                label="Course"
                onChange={(e) => setSelectedCourse(e.target.value as number)}
              >
                {mockCourses.map((course) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.code} - {course.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl sx={{ minWidth: 180 }}>
              <InputLabel>Chapter (Optional)</InputLabel>
              <Select
                value={selectedChapter}
                label="Chapter (Optional)"
                onChange={(e) => setSelectedChapter(e.target.value)}
              >
                <MenuItem value="">All Chapters</MenuItem>
                {mockChapters
                  .filter(chapter => chapter.course_id === selectedCourse)
                  .map((chapter) => (
                    <MenuItem key={chapter.id} value={chapter.id}>
                      {chapter.title}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
            
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Threshold (%)</InputLabel>
              <Select
                value={performanceThreshold}
                label="Threshold (%)"
                onChange={(e) => setPerformanceThreshold(e.target.value as number)}
              >
                <MenuItem value={30}>Below 30%</MenuItem>
                <MenuItem value={40}>Below 40%</MenuItem>
                <MenuItem value={50}>Below 50%</MenuItem>
                <MenuItem value={60}>Below 60%</MenuItem>
              </Select>
            </FormControl>

            <Tooltip title="Refresh Data">
              <IconButton 
                onClick={loadPerformanceData}
                disabled={loading}
                color="primary"
                sx={{ ml: 'auto' }}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {performanceData && (
        <>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
            gap: 3,
            mb: 4 
          }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: 2, 
                    backgroundColor: 'error.light',
                    color: 'error.contrastText'
                  }}>
                    <Person />
                  </Box>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: 'error.main' }}>
                      {performanceData.total_weak_students}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Students Need Help
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
                    backgroundColor: 'warning.light',
                    color: 'warning.contrastText'
                  }}>
                    <TaskIcon />
                  </Box>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                      {performanceData.weak_students.reduce((sum, s) => sum + s.tasks_assigned, 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tasks Assigned
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
                    <Analytics />
                  </Box>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                      {performanceData.weak_students.reduce((sum, s) => sum + s.tasks_completed, 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tasks Completed
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
                    backgroundColor: 'primary.light',
                    color: 'primary.contrastText'
                  }}>
                    <School />
                  </Box>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                      {performanceThreshold}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Performance Threshold
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Students Table */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Students Requiring Attention
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Assignment />}
                  onClick={handleAutoAssignTasks}
                  disabled={loading || performanceData.weak_students.length === 0}
                >
                  Auto-Assign Tasks
                </Button>
              </Box>

              {performanceData.weak_students.length === 0 ? (
                <Alert severity="info">
                  No students found below the performance threshold of {performanceThreshold}%
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Student</TableCell>
                        <TableCell>Chapter</TableCell>
                        <TableCell>Performance</TableCell>
                        <TableCell>Level</TableCell>
                        <TableCell>Tasks</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {performanceData.weak_students.map((student) => (
                        <TableRow key={`${student.student_id}-${student.chapter_id}`}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
                                {student.student_name.split(' ').map(n => n[0]).join('')}
                              </Avatar>
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                  {student.student_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {student.student_reg_no}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {student.chapter_title}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getPerformanceLevelIcon(student.performance_percentage)}
                              <Box sx={{ minWidth: 60 }}>
                                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                  {student.performance_percentage.toFixed(1)}%
                                </Typography>
                                <LinearProgress
                                  variant="determinate"
                                  value={student.performance_percentage}
                                  color={student.performance_percentage < 40 ? 'error' : 'warning'}
                                  sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
                                />
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={student.performance_level.replace('_', ' ')}
                              color={getPerformanceLevelColor(student.performance_level)}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {student.tasks_completed}/{student.tasks_assigned}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Completed/Assigned
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {student.needs_task_assignment ? (
                              <Chip
                                label="Needs Task"
                                color="warning"
                                size="small"
                                variant="filled"
                              />
                            ) : (
                              <Chip
                                label="Up to Date"
                                color="success"
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Assign Task">
                              <IconButton
                                size="small"
                                color="primary"
                                disabled={!student.needs_task_assignment}
                              >
                                <Assignment fontSize="small" />
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
        </>
      )}
    </Box>
  );
};

export default Performance;
