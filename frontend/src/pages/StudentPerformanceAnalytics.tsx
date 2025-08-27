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
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  School,
  Assignment,
  CheckCircle,
  Warning,
  Error,
  Timeline,
  BarChart,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface ChapterPerformance {
  chapter_id: number;
  chapter_title: string;
  course_name: string;
  cia1_score: number | null;
  cia2_score: number | null;
  cia3_score: number | null;
  final_score: number | null;
  average_score: number;
  performance_trend: string;
  is_weak_area: boolean;
  tasks_assigned: number;
  tasks_completed: number;
  improvement_percentage: number;
}

interface TaskAttempt {
  attempt_id: number;
  task_title: string;
  course_name: string;
  chapter_title: string;
  task_type: string;
  score: number;
  total_questions: number;
  percentage: number;
  attempt_date: string;
  time_taken: number;
  passed: boolean;
}

interface PerformanceTrend {
  exam_date: string;
  exam_type: string;
  course_name: string;
  percentage: number;
  chapter_count: number;
}

interface StudentPerformanceData {
  student_info: {
    student_id: number;
    name: string;
    student_reg_no: string;
    class: string;
    overall_percentage: number;
    total_weak_chapters: number;
    total_strong_chapters: number;
  };
  chapter_performance: ChapterPerformance[];
  recent_task_attempts: TaskAttempt[];
  performance_trends: PerformanceTrend[];
  summary_stats: {
    total_chapters_studied: number;
    chapters_above_average: number;
    chapters_below_average: number;
    overall_improvement: number;
    tasks_completion_rate: number;
  };
}

const StudentPerformanceAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState<StudentPerformanceData | null>(null);
  const [currentTab, setCurrentTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Mock performance data for development
  const mockPerformanceData: StudentPerformanceData = {
    student_info: {
      student_id: 1,
      name: 'Alice Johnson',
      student_reg_no: 'CS21B001',
      class: 'IV CSE A',
      overall_percentage: 67.3,
      total_weak_chapters: 4,
      total_strong_chapters: 8,
    },
    chapter_performance: [
      {
        chapter_id: 1,
        chapter_title: 'Arrays and Linked Lists',
        course_name: 'Data Structures and Algorithms',
        cia1_score: 35,
        cia2_score: 42,
        cia3_score: 38,
        final_score: null,
        average_score: 38.3,
        performance_trend: 'improving',
        is_weak_area: true,
        tasks_assigned: 3,
        tasks_completed: 2,
        improvement_percentage: 20.0,
      },
      {
        chapter_id: 2,
        chapter_title: 'Stacks and Queues',
        course_name: 'Data Structures and Algorithms',
        cia1_score: 45,
        cia2_score: 44,
        cia3_score: 46,
        final_score: null,
        average_score: 45.0,
        performance_trend: 'stable',
        is_weak_area: false,
        tasks_assigned: 1,
        tasks_completed: 1,
        improvement_percentage: 2.2,
      },
      {
        chapter_id: 3,
        chapter_title: 'Trees and Graphs',
        course_name: 'Data Structures and Algorithms',
        cia1_score: 48,
        cia2_score: 46,
        cia3_score: 44,
        final_score: null,
        average_score: 46.0,
        performance_trend: 'declining',
        is_weak_area: false,
        tasks_assigned: 0,
        tasks_completed: 0,
        improvement_percentage: -8.3,
      },
      {
        chapter_id: 4,
        chapter_title: 'SQL Basics',
        course_name: 'Database Management Systems',
        cia1_score: 42,
        cia2_score: 40,
        cia3_score: null,
        final_score: null,
        average_score: 41.0,
        performance_trend: 'declining',
        is_weak_area: true,
        tasks_assigned: 2,
        tasks_completed: 1,
        improvement_percentage: -4.8,
      },
    ],
    recent_task_attempts: [
      {
        attempt_id: 1,
        task_title: 'Arrays and Linked Lists Practice',
        course_name: 'Data Structures and Algorithms',
        chapter_title: 'Arrays and Linked Lists',
        task_type: 'frequent_assessment',
        score: 7,
        total_questions: 10,
        percentage: 70.0,
        attempt_date: '2024-01-20T14:30:00',
        time_taken: 18,
        passed: true,
      },
      {
        attempt_id: 2,
        task_title: 'Stack Operations Quiz',
        course_name: 'Data Structures and Algorithms',
        chapter_title: 'Stacks and Queues',
        task_type: 'remedial',
        score: 8,
        total_questions: 12,
        percentage: 66.7,
        attempt_date: '2024-01-18T16:45:00',
        time_taken: 15,
        passed: true,
      },
      {
        attempt_id: 3,
        task_title: 'SQL Query Practice',
        course_name: 'Database Management Systems',
        chapter_title: 'SQL Basics',
        task_type: 'frequent_assessment',
        score: 5,
        total_questions: 10,
        percentage: 50.0,
        attempt_date: '2024-01-15T10:20:00',
        time_taken: 20,
        passed: false,
      },
    ],
    performance_trends: [
      { exam_date: '2024-01-10', exam_type: 'CIA1', course_name: 'DSA', percentage: 70, chapter_count: 3 },
      { exam_date: '2024-01-15', exam_type: 'CIA1', course_name: 'DBMS', percentage: 84, chapter_count: 2 },
      { exam_date: '2024-02-10', exam_type: 'CIA2', course_name: 'DSA', percentage: 73, chapter_count: 3 },
      { exam_date: '2024-02-15', exam_type: 'CIA2', course_name: 'DBMS', percentage: 80, chapter_count: 2 },
    ],
    summary_stats: {
      total_chapters_studied: 12,
      chapters_above_average: 8,
      chapters_below_average: 4,
      overall_improvement: 5.2,
      tasks_completion_rate: 66.7,
    },
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

  useEffect(() => {
    loadPerformanceData();
  }, []);

  const getPerformanceColor = (percentage: number): 'success' | 'warning' | 'error' => {
    if (percentage >= 75) return 'success';
    if (percentage >= 50) return 'warning';
    return 'error';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp color="success" />;
      case 'declining':
        return <TrendingDown color="error" />;
      default:
        return <Timeline color="action" />;
    }
  };

  const getTrendColor = (trend: string): 'success' | 'error' | 'default' => {
    switch (trend) {
      case 'improving': return 'success';
      case 'declining': return 'error';
      default: return 'default';
    }
  };

  // Chart colors
  // const COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0'];

  if (loading && !performanceData) {
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

  if (!performanceData) return null;

  const pieChartData = [
    { name: 'Strong Chapters', value: performanceData.student_info.total_strong_chapters, color: '#4CAF50' },
    { name: 'Weak Chapters', value: performanceData.student_info.total_weak_chapters, color: '#F44336' },
  ];

  return (
    <Box sx={{ maxWidth: '100%', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 1 }}>
          My Performance Analytics 📊
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your academic progress and identify areas for improvement
        </Typography>
      </Box>

      {/* Summary Cards */}
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
                p: 1.5, 
                borderRadius: 2, 
                backgroundColor: 'primary.light',
                color: 'primary.contrastText'
              }}>
                <BarChart />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  {performanceData.student_info.overall_percentage.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overall Performance
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 2, 
                backgroundColor: 'success.light',
                color: 'success.contrastText'
              }}>
                <CheckCircle />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                  {performanceData.summary_stats.chapters_above_average}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Strong Chapters
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 2, 
                backgroundColor: 'error.light',
                color: 'error.contrastText'
              }}>
                <Warning />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'error.main' }}>
                  {performanceData.summary_stats.chapters_below_average}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Weak Chapters
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 2, 
                backgroundColor: performanceData.summary_stats.tasks_completion_rate >= 75 ? 'success.light' : 'warning.light',
                color: performanceData.summary_stats.tasks_completion_rate >= 75 ? 'success.contrastText' : 'warning.contrastText'
              }}>
                <Assignment />
              </Box>
              <Box>
                <Typography variant="h4" sx={{ 
                  fontWeight: 600, 
                  color: performanceData.summary_stats.tasks_completion_rate >= 75 ? 'success.main' : 'warning.main' 
                }}>
                  {performanceData.summary_stats.tasks_completion_rate.toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Task Completion
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Main Content */}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <School fontSize="small" />
                  Chapter Performance
                </Box>
              } />
              <Tab label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Timeline fontSize="small" />
                  Progress Trends
                </Box>
              } />
              <Tab label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Assignment fontSize="small" />
                  Recent Attempts
                </Box>
              } />
            </Tabs>
          </Box>

          {/* Chapter Performance Tab */}
          {currentTab === 0 && (
            <Box>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Chapter Details</TableCell>
                      <TableCell>CIA Scores</TableCell>
                      <TableCell>Average</TableCell>
                      <TableCell>Trend</TableCell>
                      <TableCell>Tasks</TableCell>
                      <TableCell>Improvement</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceData.chapter_performance.map((chapter) => (
                      <TableRow 
                        key={chapter.chapter_id}
                        sx={{ 
                          backgroundColor: chapter.is_weak_area ? 'error.light' : 'inherit',
                          '&:hover': { backgroundColor: 'action.hover' }
                        }}
                      >
                        <TableCell>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                              {chapter.chapter_title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {chapter.course_name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {[chapter.cia1_score, chapter.cia2_score, chapter.cia3_score].map((score, index) => (
                              <Chip
                                key={index}
                                label={score ? `${score}` : 'N/A'}
                                size="small"
                                variant="outlined"
                                color={score ? getPerformanceColor(score) : 'default'}
                                sx={{ minWidth: 50 }}
                              />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {chapter.average_score.toFixed(1)}%
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={chapter.average_score}
                              color={getPerformanceColor(chapter.average_score)}
                              sx={{ width: 60, height: 4, borderRadius: 2 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getTrendIcon(chapter.performance_trend)}
                            <Chip
                              label={chapter.performance_trend}
                              size="small"
                              color={getTrendColor(chapter.performance_trend)}
                              variant="outlined"
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {chapter.tasks_completed}/{chapter.tasks_assigned}
                          </Typography>
                          {chapter.tasks_assigned > 0 && (
                            <LinearProgress
                              variant="determinate"
                              value={(chapter.tasks_completed / chapter.tasks_assigned) * 100}
                              color="primary"
                              sx={{ width: 50, height: 3, borderRadius: 1, mt: 0.5 }}
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            color={chapter.improvement_percentage >= 0 ? 'success.main' : 'error.main'}
                            sx={{ fontWeight: 600 }}
                          >
                            {chapter.improvement_percentage > 0 ? '+' : ''}{chapter.improvement_percentage.toFixed(1)}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {chapter.is_weak_area ? (
                            <Chip label="Needs Attention" size="small" color="error" />
                          ) : (
                            <Chip label="Good" size="small" color="success" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Progress Trends Tab */}
          {currentTab === 1 && (
            <Box>
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
                gap: 3,
                mb: 3 
              }}>
                {/* Line Chart */}
                <Paper variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    Performance Trends Over Time
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData.performance_trends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="exam_date" />
                      <YAxis />
                      <RechartsTooltip 
                        labelFormatter={(value) => `Date: ${value}`}
                        formatter={(value, name) => [
                          `${value}%`, 
                          name === 'percentage' ? 'Score' : name
                        ]}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="percentage" 
                        stroke="#2196F3" 
                        strokeWidth={3}
                        dot={{ fill: '#2196F3', strokeWidth: 2, r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>

                {/* Pie Chart */}
                <Paper variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    Chapter Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Box>

              {/* Bar Chart */}
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Chapter-wise Average Scores
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsBarChart data={performanceData.chapter_performance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="chapter_title" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <RechartsTooltip 
                      formatter={(value) => [`${value}%`, 'Average Score']}
                    />
                    <Bar 
                      dataKey="average_score" 
                      fill="#4CAF50"
                      radius={[4, 4, 0, 0]}
                    />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </Paper>
            </Box>
          )}

          {/* Recent Attempts Tab */}
          {currentTab === 2 && (
            <Box>
              {performanceData.recent_task_attempts.length === 0 ? (
                <Alert severity="info">
                  No recent task attempts found. Complete some tasks to see your progress here.
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Task Details</TableCell>
                        <TableCell>Course & Chapter</TableCell>
                        <TableCell>Performance</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Date & Time</TableCell>
                        <TableCell>Result</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {performanceData.recent_task_attempts.map((attempt) => (
                        <TableRow key={attempt.attempt_id}>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                              {attempt.task_title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Time taken: {attempt.time_taken} minutes
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {attempt.course_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {attempt.chapter_title}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {attempt.score}/{attempt.total_questions}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                ({attempt.percentage.toFixed(1)}%)
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={attempt.percentage}
                              color={getPerformanceColor(attempt.percentage)}
                              sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={attempt.task_type.replace('_', ' ')}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(attempt.attempt_date).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(attempt.attempt_date).toLocaleTimeString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {attempt.passed ? (
                                <CheckCircle color="success" />
                              ) : (
                                <Error color="error" />
                              )}
                              <Chip
                                label={attempt.passed ? 'Passed' : 'Failed'}
                                size="small"
                                color={attempt.passed ? 'success' : 'error'}
                              />
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default StudentPerformanceAnalytics;
