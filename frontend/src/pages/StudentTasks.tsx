import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  LinearProgress,
  Alert,
  Avatar,
  Stack,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  PlayArrow as StartIcon,
  CheckCircle as CompleteIcon,
  Schedule as PendingIcon,
  Warning as OverdueIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';

interface Task {
  id: number;
  title: string;
  description: string;
  course: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedTime: number; // in minutes
  totalQuestions: number;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  dueDate: string;
  assignedDate: string;
  completedDate?: string;
  score?: number;
  weakChapters: string[];
  progress: number; // 0-100
}

const mockTasks: Task[] = [
  {
    id: 1,
    title: "Array Fundamentals Practice",
    description: "Practice problems on array operations, searching, and sorting algorithms",
    course: "Data Structures and Algorithms",
    difficulty: 'medium',
    estimatedTime: 30,
    totalQuestions: 10,
    status: 'pending',
    dueDate: "2024-01-30",
    assignedDate: "2024-01-25",
    weakChapters: ["Arrays", "Sorting Algorithms"],
    progress: 0
  },
  {
    id: 2,
    title: "Linked List Implementation",
    description: "Implement and test various linked list operations",
    course: "Data Structures and Algorithms",
    difficulty: 'hard',
    estimatedTime: 45,
    totalQuestions: 8,
    status: 'in_progress',
    dueDate: "2024-01-28",
    assignedDate: "2024-01-23",
    weakChapters: ["Linked Lists"],
    progress: 60
  },
  {
    id: 3,
    title: "SQL Query Practice",
    description: "Practice complex SQL queries and joins",
    course: "Database Management Systems",
    difficulty: 'medium',
    estimatedTime: 25,
    totalQuestions: 12,
    status: 'completed',
    dueDate: "2024-01-20",
    assignedDate: "2024-01-15",
    completedDate: "2024-01-19",
    score: 85,
    weakChapters: ["SQL Joins", "Subqueries"],
    progress: 100
  },
  {
    id: 4,
    title: "Tree Traversal Algorithms",
    description: "Practice different tree traversal methods and their applications",
    course: "Data Structures and Algorithms",
    difficulty: 'hard',
    estimatedTime: 40,
    totalQuestions: 15,
    status: 'overdue',
    dueDate: "2024-01-22",
    assignedDate: "2024-01-17",
    weakChapters: ["Binary Trees", "Tree Traversal"],
    progress: 0
  },
  {
    id: 5,
    title: "Network Protocols Basics",
    description: "Understanding TCP/IP, HTTP, and other fundamental protocols",
    course: "Computer Networks",
    difficulty: 'easy',
    estimatedTime: 20,
    totalQuestions: 8,
    status: 'pending',
    dueDate: "2024-02-01",
    assignedDate: "2024-01-26",
    weakChapters: ["Network Protocols"],
    progress: 0
  }
];

const StudentTasks: React.FC = () => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CompleteIcon color="success" />;
      case 'in_progress':
        return <PendingIcon color="warning" />;
      case 'overdue':
        return <OverdueIcon color="error" />;
      default:
        return <TaskIcon color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDaysRemaining = (dueDateString: string) => {
    const dueDate = new Date(dueDateString);
    const today = new Date();
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const TaskCard = ({ task }: { task: Task }) => {
    const daysRemaining = getDaysRemaining(task.dueDate);
    const isOverdue = daysRemaining < 0;
    const isDueSoon = daysRemaining <= 2 && daysRemaining >= 0;

    return (
      <Card sx={{ mb: 3, borderLeft: `4px solid ${isOverdue ? '#f44336' : isDueSoon ? '#ff9800' : '#4caf50'}` }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
              {getStatusIcon(task.status)}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                {task.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {task.course}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {task.description}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'flex-end' }}>
              <Chip 
                label={task.status.replace('_', ' ').toUpperCase()} 
                color={getStatusColor(task.status) as any}
                size="small"
              />
              <Chip 
                label={task.difficulty.toUpperCase()} 
                color={getDifficultyColor(task.difficulty) as any}
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>

          {/* Progress bar for in-progress tasks */}
          {task.status === 'in_progress' && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {task.progress}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={task.progress} 
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
          )}

          {/* Weak chapters */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Focus Areas:
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {task.weakChapters.map((chapter, index) => (
                <Chip 
                  key={index}
                  label={chapter} 
                  size="small" 
                  variant="outlined"
                  color="secondary"
                />
              ))}
            </Stack>
          </Box>

          {/* Task details */}
          <Box sx={{ display: 'flex', gap: 4, mb: 2, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TimerIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {task.estimatedTime} min
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TaskIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {task.totalQuestions} questions
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Assigned: {formatDate(task.assignedDate)}
            </Typography>
            <Typography variant="body2" color={isOverdue ? 'error.main' : 'text.secondary'}>
              Due: {formatDate(task.dueDate)}
              {isOverdue && ` (${Math.abs(daysRemaining)} days overdue)`}
              {isDueSoon && !isOverdue && ` (${daysRemaining} days left)`}
            </Typography>
          </Box>

          {/* Score for completed tasks */}
          {task.status === 'completed' && task.score && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Completed!</strong> You scored {task.score}% on {formatDate(task.completedDate!)}
              </Typography>
            </Alert>
          )}

          {/* Overdue warning */}
          {task.status === 'overdue' && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Overdue!</strong> This task was due {Math.abs(daysRemaining)} days ago. Please complete it as soon as possible.
              </Typography>
            </Alert>
          )}

          {/* Action buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            {task.status === 'pending' && (
              <Button 
                variant="contained" 
                startIcon={<StartIcon />}
                color="primary"
              >
                Start Task
              </Button>
            )}
            {task.status === 'in_progress' && (
              <Button 
                variant="contained" 
                startIcon={<StartIcon />}
                color="warning"
              >
                Continue
              </Button>
            )}
            {task.status === 'overdue' && (
              <Button 
                variant="contained" 
                startIcon={<StartIcon />}
                color="error"
              >
                Start Now
              </Button>
            )}
            {task.status === 'completed' && (
              <Button 
                variant="outlined" 
                color="primary"
              >
                Review
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Group tasks by status
  const pendingTasks = mockTasks.filter(t => t.status === 'pending');
  const inProgressTasks = mockTasks.filter(t => t.status === 'in_progress');
  const overdueTasks = mockTasks.filter(t => t.status === 'overdue');
  const completedTasks = mockTasks.filter(t => t.status === 'completed');

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
        My Tasks
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Personalized learning tasks based on your performance analysis
      </Typography>

      {/* Task statistics */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 4 }}>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h3" color="warning.main" sx={{ fontWeight: 600 }}>
            {pendingTasks.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Pending Tasks
          </Typography>
        </Card>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h3" color="info.main" sx={{ fontWeight: 600 }}>
            {inProgressTasks.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            In Progress
          </Typography>
        </Card>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h3" color="error.main" sx={{ fontWeight: 600 }}>
            {overdueTasks.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Overdue
          </Typography>
        </Card>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h3" color="success.main" sx={{ fontWeight: 600 }}>
            {completedTasks.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Completed
          </Typography>
        </Card>
      </Box>

      {/* Overdue tasks - highest priority */}
      {overdueTasks.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 2, color: 'error.main' }}>
            ⚠️ Overdue Tasks
          </Typography>
          {overdueTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </Box>
      )}

      {/* In progress tasks */}
      {inProgressTasks.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
            🔄 In Progress
          </Typography>
          {inProgressTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </Box>
      )}

      {/* Pending tasks */}
      {pendingTasks.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
            📋 Pending Tasks
          </Typography>
          {pendingTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </Box>
      )}

      {/* Completed tasks */}
      {completedTasks.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
            ✅ Completed Tasks
          </Typography>
          {completedTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </Box>
      )}

      {mockTasks.length === 0 && (
        <Alert severity="info">
          <Typography variant="body1">
            No tasks assigned yet. Tasks will be automatically generated based on your CIA exam performance to help you improve in weak areas.
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default StudentTasks;
