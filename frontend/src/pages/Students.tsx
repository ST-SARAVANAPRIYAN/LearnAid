import React, { useEffect, useState } from 'react';
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
  TextField,
  MenuItem,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  LinearProgress,
  Stack,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
  Grade as GradeIcon,
} from '@mui/icons-material';
import { facultyService } from '../services/api';

interface Course {
  id: number;
  name: string;
  code: string;
}

interface Student {
  id: number;
  full_name: string;
  email: string;
  roll_number: string;
  department: string;
  semester: number;
  avatar?: string;
}

interface StudentPerformance {
  student_id: number;
  student_name: string;
  course_id: number;
  course_name: string;
  total_marks: number;
  obtained_marks: number;
  percentage: number;
  grade: string;
  chapter_wise_performance: {
    chapter: string;
    marks_obtained: number;
    total_marks: number;
    percentage: number;
  }[];
}

const Students: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [students, setStudents] = useState<Student[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [studentPerformance, setStudentPerformance] = useState<StudentPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [performanceDialogOpen, setPerformanceDialogOpen] = useState(false);

  // Mock data for development
  const mockStudents: Student[] = [
    {
      id: 1,
      full_name: "Alice Johnson",
      email: "alice.johnson@example.com",
      roll_number: "CS21001",
      department: "Computer Science",
      semester: 6,
    },
    {
      id: 2,
      full_name: "Bob Smith",
      email: "bob.smith@example.com",
      roll_number: "CS21002",
      department: "Computer Science",
      semester: 6,
    },
    {
      id: 3,
      full_name: "Carol Davis",
      email: "carol.davis@example.com",
      roll_number: "CS21003",
      department: "Computer Science",
      semester: 6,
    },
    {
      id: 4,
      full_name: "David Wilson",
      email: "david.wilson@example.com",
      roll_number: "CS21004",
      department: "Computer Science",
      semester: 6,
    },
    {
      id: 5,
      full_name: "Eva Brown",
      email: "eva.brown@example.com",
      roll_number: "CS21005",
      department: "Computer Science",
      semester: 6,
    },
  ];

  const mockPerformanceData = [
    { course: 'Machine Learning', students: 45, avgPerformance: 85, topPerformer: 'Alice Johnson' },
    { course: 'Data Structures', students: 52, avgPerformance: 82, topPerformer: 'Bob Smith' },
    { course: 'Web Development', students: 38, avgPerformance: 88, topPerformer: 'Carol Davis' },
    { course: 'Database Systems', students: 41, avgPerformance: 79, topPerformer: 'David Wilson' },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const coursesResponse = await facultyService.getCourses();
      setCourses(coursesResponse.data);
      
      // Use mock data for development
      setStudents(mockStudents);
    } catch (err: any) {
      setError('Failed to fetch data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async (courseId?: string) => {
    try {
      if (courseId) {
        const response = await facultyService.getStudents(parseInt(courseId));
        setStudents(response.data);
      } else {
        // Use mock data for development
        setStudents(mockStudents);
      }
    } catch (err: any) {
      setError('Failed to fetch students');
      console.error('Students fetch error:', err);
    }
  };

  const fetchStudentPerformance = async (studentId: number, courseId?: number) => {
    try {
      if (courseId) {
        const response = await facultyService.getStudentPerformance(courseId, studentId);
        setStudentPerformance(response.data);
      } else {
        // Mock performance data
        const mockPerformance: StudentPerformance = {
          student_id: studentId,
          student_name: selectedStudent?.full_name || '',
          course_id: 1,
          course_name: 'Machine Learning',
          total_marks: 100,
          obtained_marks: 85,
          percentage: 85,
          grade: 'A',
          chapter_wise_performance: [
            { chapter: 'Introduction to ML', marks_obtained: 18, total_marks: 20, percentage: 90 },
            { chapter: 'Supervised Learning', marks_obtained: 22, total_marks: 25, percentage: 88 },
            { chapter: 'Unsupervised Learning', marks_obtained: 20, total_marks: 25, percentage: 80 },
            { chapter: 'Neural Networks', marks_obtained: 25, total_marks: 30, percentage: 83 },
          ],
        };
        setStudentPerformance(mockPerformance);
      }
    } catch (err: any) {
      setError('Failed to fetch performance data');
      console.error('Performance fetch error:', err);
    }
  };

  const handleCourseChange = (courseId: string) => {
    setSelectedCourse(courseId);
    fetchStudents(courseId || undefined);
  };

  const handleViewPerformance = (student: Student) => {
    setSelectedStudent(student);
    fetchStudentPerformance(student.id, selectedCourse ? parseInt(selectedCourse) : undefined);
    setPerformanceDialogOpen(true);
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'success';
      case 'B': return 'info';
      case 'C': return 'warning';
      case 'D': return 'error';
      default: return 'default';
    }
  };

  const getPerformanceColor = (percentage: number) => {
    if (percentage >= 85) return '#4caf50';
    if (percentage >= 70) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Students Management
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab 
          label="All Students" 
          icon={<PersonIcon />} 
          iconPosition="start"
        />
        <Tab 
          label="Performance Overview" 
          icon={<AssessmentIcon />} 
          iconPosition="start"
        />
      </Tabs>

      {/* Students List Tab */}
      {tabValue === 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
              <Typography variant="h6">Students List</Typography>
              <TextField
                select
                label="Filter by Course"
                value={selectedCourse}
                onChange={(e) => handleCourseChange(e.target.value)}
                sx={{ minWidth: 200 }}
                size="small"
              >
                <MenuItem value="">All Courses</MenuItem>
                {courses.map((course) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.code} - {course.name}
                  </MenuItem>
                ))}
              </TextField>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Roll Number</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Semester</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                            {student.full_name.charAt(0)}
                          </Avatar>
                          <Typography variant="body2" fontWeight="medium">
                            {student.full_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{student.roll_number}</TableCell>
                      <TableCell>{student.email}</TableCell>
                      <TableCell>{student.department}</TableCell>
                      <TableCell>{student.semester}</TableCell>
                      <TableCell>
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewPerformance(student)}
                          title="View Performance"
                        >
                          <ViewIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Performance Overview Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Course-wise Performance Overview
            </Typography>

            <Box sx={{ mt: 3 }}>
              {mockPerformanceData.map((course, index) => (
                <Card key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {course.course}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {course.students} students enrolled
                        </Typography>
                      </Box>
                      <Box textAlign="right">
                        <Typography variant="h5" sx={{ color: getPerformanceColor(course.avgPerformance) }}>
                          {course.avgPerformance}%
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Average Performance
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Box sx={{ mt: 2 }}>
                      <LinearProgress
                        variant="determinate"
                        value={course.avgPerformance}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          bgcolor: 'grey.200',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 4,
                            bgcolor: getPerformanceColor(course.avgPerformance),
                          },
                        }}
                      />
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mt: 2 }}>
                      <Box display="flex" alignItems="center">
                        <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                        <Typography variant="body2">
                          Top Performer: <strong>{course.topPerformer}</strong>
                        </Typography>
                      </Box>
                      <Chip
                        label={course.avgPerformance >= 85 ? 'Excellent' : 
                              course.avgPerformance >= 70 ? 'Good' : 'Needs Improvement'}
                        color={course.avgPerformance >= 85 ? 'success' : 
                               course.avgPerformance >= 70 ? 'info' : 'error'}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Student Performance Dialog */}
      <Dialog 
        open={performanceDialogOpen} 
        onClose={() => setPerformanceDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
              {selectedStudent?.full_name.charAt(0)}
            </Avatar>
            <Box>
              <Typography variant="h6">{selectedStudent?.full_name}</Typography>
              <Typography variant="body2" color="textSecondary">
                {selectedStudent?.roll_number} • Performance Details
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {studentPerformance && (
            <Stack spacing={3}>
              {/* Overall Performance */}
              <Card sx={{ bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="h6">{studentPerformance.course_name}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        Overall Performance
                      </Typography>
                    </Box>
                    <Box textAlign="right">
                      <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                        {studentPerformance.percentage}%
                      </Typography>
                      <Chip 
                        label={`Grade: ${studentPerformance.grade}`} 
                        color={getGradeColor(studentPerformance.grade) as any}
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      {studentPerformance.obtained_marks} / {studentPerformance.total_marks} marks
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={studentPerformance.percentage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          bgcolor: 'primary.main',
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>

              {/* Chapter-wise Performance */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  Chapter-wise Performance
                </Typography>
                <List>
                  {studentPerformance.chapter_wise_performance.map((chapter, index) => (
                    <ListItem key={index}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getPerformanceColor(chapter.percentage) }}>
                          <GradeIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={chapter.chapter}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              {chapter.marks_obtained} / {chapter.total_marks} marks
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={chapter.percentage}
                              sx={{
                                mt: 1,
                                height: 6,
                                borderRadius: 3,
                                bgcolor: 'grey.200',
                                '& .MuiLinearProgress-bar': {
                                  borderRadius: 3,
                                  bgcolor: getPerformanceColor(chapter.percentage),
                                },
                              }}
                            />
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Chip
                          label={`${chapter.percentage}%`}
                          size="small"
                          sx={{
                            bgcolor: getPerformanceColor(chapter.percentage),
                            color: 'white',
                            fontWeight: 'bold',
                          }}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Stack>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setPerformanceDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Students;
