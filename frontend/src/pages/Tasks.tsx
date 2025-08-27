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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Fab,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  Assignment,
  Timer,
  People,
  Edit,
  Delete,
  Visibility,
  AutoMode,
} from '@mui/icons-material';

interface Task {
  id: number;
  title: string;
  description: string;
  course_id: number;
  course_name: string;
  chapter_id: number;
  chapter_title: string;
  task_type: string;
  difficulty_level: string;
  total_questions: number;
  time_limit_minutes: number;
  is_auto_generated: boolean;
  is_published: boolean;
  target_performance_threshold: number;
  assigned_students: number;
  completed_students: number;
  created_at: string;
}

const Tasks: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [currentTab, setCurrentTab] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    course_id: '',
    chapter_id: '',
    task_type: 'frequent_assessment',
    difficulty_level: 'medium',
    time_limit_minutes: 20,
    target_performance_threshold: 50,
  });

  // Mock data
  const mockCourses = [
    { id: 1, name: 'Data Structures and Algorithms', code: 'CS301' },
    { id: 2, name: 'Database Management Systems', code: 'CS302' },
  ];

  const mockChapters = [
    { id: 1, title: 'Arrays and Linked Lists', course_id: 1 },
    { id: 2, title: 'Stacks and Queues', course_id: 1 },
    { id: 3, title: 'Trees and Graphs', course_id: 1 },
  ];

  const mockTasks: Task[] = [
    {
      id: 1,
      title: 'Arrays Practice Assessment',
      description: 'Frequent assessment for students struggling with arrays and linked lists',
      course_id: 1,
      course_name: 'Data Structures and Algorithms',
      chapter_id: 1,
      chapter_title: 'Arrays and Linked Lists',
      task_type: 'frequent_assessment',
      difficulty_level: 'medium',
      total_questions: 10,
      time_limit_minutes: 20,
      is_auto_generated: true,
      is_published: true,
      target_performance_threshold: 50.0,
      assigned_students: 5,
      completed_students: 3,
      created_at: '2024-01-20',
    },
    {
      id: 2,
      title: 'Stack Operations Quiz',
      description: 'Manual assessment for stack and queue concepts',
      course_id: 1,
      course_name: 'Data Structures and Algorithms',
      chapter_id: 2,
      chapter_title: 'Stacks and Queues',
      task_type: 'bi_daily',
      difficulty_level: 'easy',
      total_questions: 8,
      time_limit_minutes: 15,
      is_auto_generated: false,
      is_published: true,
      target_performance_threshold: 40.0,
      assigned_students: 3,
      completed_students: 1,
      created_at: '2024-01-18',
    },
    {
      id: 3,
      title: 'Tree Traversal Challenge',
      description: 'Advanced assessment for tree concepts',
      course_id: 1,
      course_name: 'Data Structures and Algorithms',
      chapter_id: 3,
      chapter_title: 'Trees and Graphs',
      task_type: 'remedial',
      difficulty_level: 'hard',
      total_questions: 12,
      time_limit_minutes: 30,
      is_auto_generated: false,
      is_published: false,
      target_performance_threshold: 60.0,
      assigned_students: 0,
      completed_students: 0,
      created_at: '2024-01-22',
    },
  ];

  const loadTasks = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      setTasks(mockTasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newTaskData: Task = {
        id: Date.now(),
        title: newTask.title,
        description: newTask.description,
        course_id: parseInt(newTask.course_id),
        course_name: mockCourses.find(c => c.id === parseInt(newTask.course_id))?.name || '',
        chapter_id: parseInt(newTask.chapter_id),
        chapter_title: mockChapters.find(c => c.id === parseInt(newTask.chapter_id))?.title || '',
        task_type: newTask.task_type,
        difficulty_level: newTask.difficulty_level,
        total_questions: 0,
        time_limit_minutes: newTask.time_limit_minutes,
        is_auto_generated: false,
        is_published: false,
        target_performance_threshold: newTask.target_performance_threshold,
        assigned_students: 0,
        completed_students: 0,
        created_at: new Date().toISOString().split('T')[0],
      };
      
      setTasks(prev => [newTaskData, ...prev]);
      setCreateDialogOpen(false);
      setNewTask({
        title: '',
        description: '',
        course_id: '',
        chapter_id: '',
        task_type: 'frequent_assessment',
        difficulty_level: 'medium',
        time_limit_minutes: 20,
        target_performance_threshold: 50,
      });
      
      alert('Task created successfully!');
    } catch (error) {
      console.error('Error creating task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoGenerateTask = async () => {
    try {
      alert('Auto-generate task feature will use LLM to create questions from PDF content!');
      // This would integrate with the LLM API
    } catch (error) {
      console.error('Error auto-generating task:', error);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'frequent_assessment': return 'primary';
      case 'daily': return 'success';
      case 'bi_daily': return 'info';
      case 'remedial': return 'warning';
      default: return 'default';
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const filteredTasks = () => {
    switch (currentTab) {
      case 0: return tasks; // All tasks
      case 1: return tasks.filter(t => t.is_published); // Published
      case 2: return tasks.filter(t => !t.is_published); // Draft
      case 3: return tasks.filter(t => t.is_auto_generated); // Auto-generated
      default: return tasks;
    }
  };

  if (loading && tasks.length === 0) {
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
          📋 Task Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Create and manage frequent assessments and remedial tasks for students
        </Typography>
      </Box>

      {/* Summary Cards */}
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
                backgroundColor: 'primary.light',
                color: 'primary.contrastText'
              }}>
                <Assignment />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  {tasks.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Tasks
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
                <Visibility />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                  {tasks.filter(t => t.is_published).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Published
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
                <People />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                  {tasks.reduce((sum, t) => sum + t.assigned_students, 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Assigned Students
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
                backgroundColor: 'info.light',
                color: 'info.contrastText'
              }}>
                <AutoMode />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                  {tasks.filter(t => t.is_auto_generated).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  AI Generated
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Tasks Table */}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab label={`All Tasks (${tasks.length})`} />
              <Tab label={`Published (${tasks.filter(t => t.is_published).length})`} />
              <Tab label={`Draft (${tasks.filter(t => !t.is_published).length})`} />
              <Tab label={`AI Generated (${tasks.filter(t => t.is_auto_generated).length})`} />
            </Tabs>
          </Box>

          {filteredTasks().length === 0 ? (
            <Alert severity="info">
              No tasks found in this category.
            </Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Task</TableCell>
                    <TableCell>Course & Chapter</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Difficulty</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Students</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredTasks().map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {task.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {task.description.length > 50 
                              ? `${task.description.substring(0, 50)}...` 
                              : task.description}
                          </Typography>
                          {task.is_auto_generated && (
                            <Chip
                              size="small"
                              icon={<AutoMode />}
                              label="AI"
                              color="info"
                              variant="outlined"
                              sx={{ ml: 1, mt: 0.5 }}
                            />
                          )}
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
                          label={task.task_type.replace('_', ' ')}
                          color={getTaskTypeColor(task.task_type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.difficulty_level}
                          color={getDifficultyColor(task.difficulty_level)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Timer fontSize="small" color="action" />
                          <Typography variant="body2">
                            {task.time_limit_minutes}m
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {task.completed_students}/{task.assigned_students}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Completed/Assigned
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.is_published ? 'Published' : 'Draft'}
                          color={task.is_published ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Task">
                            <IconButton size="small" color="warning">
                              <Edit fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Task">
                            <IconButton size="small" color="error">
                              <Delete fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Floating Action Buttons */}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Tooltip title="Auto-Generate Task with AI">
          <Fab color="secondary" onClick={handleAutoGenerateTask}>
            <AutoMode />
          </Fab>
        </Tooltip>
        <Tooltip title="Create New Task">
          <Fab color="primary" onClick={() => setCreateDialogOpen(true)}>
            <Add />
          </Fab>
        </Tooltip>
      </Box>

      {/* Create Task Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
            <TextField
              label="Task Title"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              fullWidth
              required
            />
            
            <TextField
              label="Description"
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Course</InputLabel>
                <Select
                  value={newTask.course_id}
                  label="Course"
                  onChange={(e) => setNewTask({ ...newTask, course_id: e.target.value, chapter_id: '' })}
                >
                  {mockCourses.map((course) => (
                    <MenuItem key={course.id} value={course.id}>
                      {course.code} - {course.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Chapter</InputLabel>
                <Select
                  value={newTask.chapter_id}
                  label="Chapter"
                  onChange={(e) => setNewTask({ ...newTask, chapter_id: e.target.value })}
                  disabled={!newTask.course_id}
                >
                  {mockChapters
                    .filter(chapter => chapter.course_id === parseInt(newTask.course_id))
                    .map((chapter) => (
                      <MenuItem key={chapter.id} value={chapter.id}>
                        {chapter.title}
                      </MenuItem>
                    ))}
                </Select>
              </FormControl>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ minWidth: 150 }}>
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={newTask.task_type}
                  label="Task Type"
                  onChange={(e) => setNewTask({ ...newTask, task_type: e.target.value })}
                >
                  <MenuItem value="frequent_assessment">Frequent Assessment</MenuItem>
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="bi_daily">Bi-Daily</MenuItem>
                  <MenuItem value="remedial">Remedial</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl sx={{ minWidth: 150 }}>
                <InputLabel>Difficulty</InputLabel>
                <Select
                  value={newTask.difficulty_level}
                  label="Difficulty"
                  onChange={(e) => setNewTask({ ...newTask, difficulty_level: e.target.value })}
                >
                  <MenuItem value="easy">Easy</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="hard">Hard</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                label="Time Limit (minutes)"
                type="number"
                value={newTask.time_limit_minutes}
                onChange={(e) => setNewTask({ ...newTask, time_limit_minutes: parseInt(e.target.value) })}
                sx={{ minWidth: 150 }}
              />
            </Box>
            
            <TextField
              label="Performance Threshold (%)"
              type="number"
              value={newTask.target_performance_threshold}
              onChange={(e) => setNewTask({ ...newTask, target_performance_threshold: parseFloat(e.target.value) })}
              helperText="Students below this performance level will be assigned this task"
              InputProps={{ inputProps: { min: 0, max: 100 } }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateTask}
            variant="contained"
            disabled={!newTask.title || !newTask.course_id || !newTask.chapter_id}
          >
            Create Task
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Tasks;
