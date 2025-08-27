import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Avatar,
  Button,
} from '@mui/material';
import {
  School as SchoolIcon,
  PlayArrow as StartIcon,
} from '@mui/icons-material';

interface Course {
  id: number;
  name: string;
  department: string;
  instructor: string;
  description: string;
  totalChapters: number;
  completedChapters: number;
  totalTasks: number;
  completedTasks: number;
  overallScore: number;
  lastActivity: string;
  color: string;
}

const mockCourses: Course[] = [
  {
    id: 1,
    name: "Data Structures and Algorithms",
    department: "Computer Science",
    instructor: "Dr. Sarah Wilson",
    description: "Fundamental concepts of data structures, algorithms, and their analysis",
    totalChapters: 12,
    completedChapters: 8,
    totalTasks: 24,
    completedTasks: 18,
    overallScore: 85,
    lastActivity: "2 hours ago",
    color: "#4fc3f7"
  },
  {
    id: 2,
    name: "Database Management Systems",
    department: "Computer Science",
    instructor: "Prof. Michael Chen",
    description: "Design and implementation of database systems",
    totalChapters: 10,
    completedChapters: 6,
    totalTasks: 20,
    completedTasks: 12,
    overallScore: 78,
    lastActivity: "1 day ago",
    color: "#81c784"
  },
  {
    id: 3,
    name: "Computer Networks",
    department: "Computer Science",
    instructor: "Dr. Lisa Anderson",
    description: "Principles of computer networking and communication protocols",
    totalChapters: 8,
    completedChapters: 3,
    totalTasks: 16,
    completedTasks: 6,
    overallScore: 65,
    lastActivity: "3 days ago",
    color: "#ffb74d"
  }
];

const StudentCourses: React.FC = () => {
  const CourseCard = ({ course }: { course: Course }) => {
    const progressPercentage = (course.completedChapters / course.totalChapters) * 100;
    const taskProgressPercentage = (course.completedTasks / course.totalTasks) * 100;

    return (
      <Card 
        sx={{ 
          mb: 3,
          transition: 'all 0.3s ease',
          '&:hover': { 
            transform: 'translateY(-4px)', 
            boxShadow: 6 
          },
          borderLeft: `4px solid ${course.color}`,
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Avatar sx={{ bgcolor: course.color, width: 48, height: 48 }}>
              <SchoolIcon />
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                {course.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {course.instructor} • {course.department}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {course.description}
              </Typography>
            </Box>
            <Chip 
              label={`${course.overallScore}%`} 
              color={course.overallScore >= 80 ? 'success' : course.overallScore >= 60 ? 'warning' : 'error'}
              size="small"
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Chapter Progress
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {course.completedChapters}/{course.totalChapters}
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progressPercentage} 
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Task Progress
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {course.completedTasks}/{course.totalTasks}
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={taskProgressPercentage} 
              sx={{ height: 6, borderRadius: 3 }}
              color="secondary"
            />
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Last activity: {course.lastActivity}
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              startIcon={<StartIcon />}
              sx={{ borderColor: course.color, color: course.color }}
            >
              Continue
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
        My Courses
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Track your progress across all enrolled courses
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 3 }}>
        {mockCourses.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </Box>
    </Box>
  );
};

export default StudentCourses;
