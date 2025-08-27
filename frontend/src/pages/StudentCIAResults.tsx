import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Assessment as ExamIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';

interface CIAResult {
  id: number;
  examType: string;
  course: string;
  totalMarks: number;
  obtainedMarks: number;
  percentage: number;
  grade: string;
  date: string;
  chapters: {
    name: string;
    marks: number;
    total: number;
    percentage: number;
  }[];
}

const mockCIAResults: CIAResult[] = [
  {
    id: 1,
    examType: "CIA 1",
    course: "Data Structures and Algorithms",
    totalMarks: 50,
    obtainedMarks: 42,
    percentage: 84,
    grade: "A",
    date: "2024-01-15",
    chapters: [
      { name: "Arrays", marks: 8, total: 10, percentage: 80 },
      { name: "Linked Lists", marks: 9, total: 10, percentage: 90 },
      { name: "Stacks & Queues", marks: 7, total: 10, percentage: 70 },
      { name: "Trees", marks: 18, total: 20, percentage: 90 },
    ]
  },
  {
    id: 2,
    examType: "CIA 2",
    course: "Data Structures and Algorithms",
    totalMarks: 50,
    obtainedMarks: 38,
    percentage: 76,
    grade: "B+",
    date: "2024-02-20",
    chapters: [
      { name: "Hash Tables", marks: 7, total: 10, percentage: 70 },
      { name: "Graphs", marks: 8, total: 10, percentage: 80 },
      { name: "Dynamic Programming", marks: 6, total: 10, percentage: 60 },
      { name: "Algorithms", marks: 17, total: 20, percentage: 85 },
    ]
  },
  {
    id: 3,
    examType: "CIA 1",
    course: "Database Management Systems",
    totalMarks: 50,
    obtainedMarks: 39,
    percentage: 78,
    grade: "B+",
    date: "2024-01-18",
    chapters: [
      { name: "ER Model", marks: 9, total: 10, percentage: 90 },
      { name: "Relational Model", marks: 8, total: 10, percentage: 80 },
      { name: "SQL Basics", marks: 6, total: 10, percentage: 60 },
      { name: "Normalization", marks: 16, total: 20, percentage: 80 },
    ]
  }
];

const StudentCIAResults: React.FC = () => {
  const getGradeColor = (percentage: number) => {
    if (percentage >= 90) return 'success';
    if (percentage >= 80) return 'info';
    if (percentage >= 70) return 'warning';
    if (percentage >= 60) return 'secondary';
    return 'error';
  };

  const getPerformanceTrend = (results: CIAResult[], course: string) => {
    const courseResults = results.filter(r => r.course === course).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    if (courseResults.length < 2) return null;
    
    const latest = courseResults[courseResults.length - 1];
    const previous = courseResults[courseResults.length - 2];
    const trend = latest.percentage - previous.percentage;
    
    return {
      trend,
      icon: trend > 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />,
      text: trend > 0 ? `+${trend.toFixed(1)}%` : `${trend.toFixed(1)}%`,
      color: trend > 0 ? 'success' : 'error'
    };
  };

  const courses = [...new Set(mockCIAResults.map(r => r.course))];

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
        CIA Results
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        View your CIA exam results and chapter-wise performance analysis
      </Typography>

      {/* Overall Performance Summary */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 3, mb: 4 }}>
        {courses.map(course => {
          const courseResults = mockCIAResults.filter(r => r.course === course);
          const avgPercentage = courseResults.reduce((sum, r) => sum + r.percentage, 0) / courseResults.length;
          const trend = getPerformanceTrend(mockCIAResults, course);
          
          return (
            <Card key={course}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <ExamIcon color="primary" />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {course}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {courseResults.length} CIA exams completed
                    </Typography>
                  </Box>
                  {trend && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {trend.icon}
                      <Typography variant="caption" color={`${trend.color}.main`}>
                        {trend.text}
                      </Typography>
                    </Box>
                  )}
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Average Performance
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {avgPercentage.toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={avgPercentage} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={getGradeColor(avgPercentage)}
                  />
                </Box>
              </CardContent>
            </Card>
          );
        })}
      </Box>

      {/* Detailed Results */}
      {courses.map(course => {
        const courseResults = mockCIAResults.filter(r => r.course === course);
        
        return (
          <Card key={course} sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                {course} - CIA Results
              </Typography>
              
              {courseResults.map(result => (
                <Box key={result.id} sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {result.examType} - {new Date(result.date).toLocaleDateString()}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {result.obtainedMarks}/{result.totalMarks}
                      </Typography>
                      <Chip 
                        label={`${result.percentage}% (${result.grade})`} 
                        color={getGradeColor(result.percentage)}
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Chapter-wise Performance Analysis:</strong> Review your performance in each chapter to identify areas for improvement.
                    </Typography>
                  </Alert>
                  
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Chapter</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600 }}>Marks Obtained</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600 }}>Total Marks</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600 }}>Percentage</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600 }}>Performance</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.chapters.map((chapter, index) => (
                          <TableRow key={index} sx={{ '&:hover': { backgroundColor: 'action.hover' } }}>
                            <TableCell>{chapter.name}</TableCell>
                            <TableCell align="center">{chapter.marks}</TableCell>
                            <TableCell align="center">{chapter.total}</TableCell>
                            <TableCell align="center">{chapter.percentage}%</TableCell>
                            <TableCell align="center">
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={chapter.percentage} 
                                  sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                                  color={getGradeColor(chapter.percentage)}
                                />
                                <Chip 
                                  label={chapter.percentage >= 80 ? 'Strong' : chapter.percentage >= 60 ? 'Good' : 'Needs Improvement'} 
                                  size="small"
                                  color={getGradeColor(chapter.percentage)}
                                  sx={{ minWidth: 120 }}
                                />
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              ))}
            </CardContent>
          </Card>
        );
      })}
    </Box>
  );
};

export default StudentCIAResults;
