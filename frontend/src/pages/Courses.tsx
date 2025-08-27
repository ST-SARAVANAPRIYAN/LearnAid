import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  Fab,
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  MenuBook as MenuBookIcon,
} from '@mui/icons-material';

interface Course {
  id: number;
  name: string;
  code: string;
  department: string;
  overview: string;
  faculty_id: number;
  is_active: boolean;
  created_at: string;
  chapters_count?: number;
  students_count?: number;
}

const Courses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    department: '',
    overview: '',
  });

  // Mock data for development
  const mockCourses: Course[] = [
    {
      id: 1,
      name: 'Introduction to Machine Learning',
      code: 'CS301ML',
      department: 'Computer Science',
      overview: 'Comprehensive introduction to machine learning algorithms, supervised and unsupervised learning, and practical applications.',
      faculty_id: 1,
      is_active: true,
      created_at: '2024-01-15',
      chapters_count: 8,
      students_count: 45,
    },
    {
      id: 2,
      name: 'Data Structures and Algorithms',
      code: 'CS201DSA',
      department: 'Computer Science',
      overview: 'Advanced data structures, algorithm design and analysis, complexity theory, and optimization techniques.',
      faculty_id: 1,
      is_active: true,
      created_at: '2024-02-01',
      chapters_count: 12,
      students_count: 67,
    },
    {
      id: 3,
      name: 'Database Management Systems',
      code: 'CS401DB',
      department: 'Computer Science',
      overview: 'Relational databases, SQL, normalization, transaction management, and database design principles.',
      faculty_id: 1,
      is_active: true,
      created_at: '2024-01-20',
      chapters_count: 10,
      students_count: 52,
    },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setCourses(mockCourses);
      setLoading(false);
    }, 1000);
  }, []);

  const handleOpenDialog = (course?: Course) => {
    if (course) {
      setEditingCourse(course);
      setFormData({
        name: course.name,
        code: course.code,
        department: course.department,
        overview: course.overview,
      });
    } else {
      setEditingCourse(null);
      setFormData({
        name: '',
        code: '',
        department: '',
        overview: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCourse(null);
    setFormData({
      name: '',
      code: '',
      department: '',
      overview: '',
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingCourse) {
        // Update existing course
        const updatedCourses = courses.map(course =>
          course.id === editingCourse.id
            ? { ...course, ...formData }
            : course
        );
        setCourses(updatedCourses);
      } else {
        // Create new course
        const newCourse: Course = {
          id: Date.now(),
          ...formData,
          faculty_id: 1,
          is_active: true,
          created_at: new Date().toISOString().split('T')[0],
          chapters_count: 0,
          students_count: 0,
        };
        setCourses([...courses, newCourse]);
      }
      handleCloseDialog();
    } catch (err) {
      setError('Failed to save course');
    }
  };

  const handleDelete = async (courseId: number) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      setCourses(courses.filter(course => course.id !== courseId));
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Courses
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          📚 Course Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Create Course
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Course Statistics */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 4 }}>
        <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {courses.length}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Courses
                </Typography>
              </Box>
              <SchoolIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {courses.reduce((sum, course) => sum + (course.students_count || 0), 0)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Students
                </Typography>
              </Box>
              <PeopleIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {courses.reduce((sum, course) => sum + (course.chapters_count || 0), 0)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Chapters
                </Typography>
              </Box>
              <MenuBookIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {courses.filter(course => course.is_active).length}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Active Courses
                </Typography>
              </Box>
              <SchoolIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Courses Grid */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 3 }}>
        {courses.map((course) => (
          <Card key={course.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold' }}>
                    {course.name}
                  </Typography>
                  <Chip
                    label={course.is_active ? 'Active' : 'Inactive'}
                    color={course.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="primary" sx={{ fontWeight: 'medium', mb: 1 }}>
                  {course.code}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Department: {course.department}
                </Typography>
                
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {course.overview.length > 150 
                    ? `${course.overview.substring(0, 150)}...` 
                    : course.overview}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <MenuBookIcon color="primary" fontSize="small" />
                    <Typography variant="body2">
                      {course.chapters_count || 0} chapters
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <PeopleIcon color="primary" fontSize="small" />
                    <Typography variant="body2">
                      {course.students_count || 0} students
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="caption" color="text.secondary">
                  Created: {new Date(course.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>
              
              <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                <Box>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleOpenDialog(course)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(course.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={() => console.log('Upload chapters for course:', course.id)}
                >
                  Upload Chapters
                </Button>
            </CardActions>
          </Card>
        ))}
      </Box>      {/* Create/Edit Course Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCourse ? 'Edit Course' : 'Create New Course'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Stack spacing={3}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Course Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <TextField
                  fullWidth
                  label="Course Code"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  required
                />
              </Box>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={formData.department}
                  label="Department"
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                >
                  <MenuItem value="Computer Science">Computer Science</MenuItem>
                  <MenuItem value="Information Technology">Information Technology</MenuItem>
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Mechanical">Mechanical</MenuItem>
                  <MenuItem value="Civil">Civil</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Course Overview"
                value={formData.overview}
                onChange={(e) => setFormData({ ...formData, overview: e.target.value })}
                multiline
                rows={4}
                required
              />
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.name || !formData.code || !formData.department}
          >
            {editingCourse ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for mobile */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', sm: 'none' },
        }}
        onClick={() => handleOpenDialog()}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default Courses;
