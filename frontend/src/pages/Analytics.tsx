import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Tabs,
  Tab,
  Stack,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
} from '@mui/material';
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
  Area,
  AreaChart,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  School as SchoolIcon,
  Quiz as QuizIcon,
  People as PeopleIcon,
} from '@mui/icons-material';

// Mock data for analytics
const performanceData = [
  { course: 'Machine Learning', avgScore: 85, students: 45, improvement: 8 },
  { course: 'Data Structures', avgScore: 82, students: 52, improvement: 5 },
  { course: 'Web Development', avgScore: 88, students: 38, improvement: 12 },
  { course: 'Database Systems', avgScore: 79, students: 41, improvement: -2 },
  { course: 'Algorithms', avgScore: 83, students: 36, improvement: 7 },
];

const trendData = [
  { month: 'Jan', performance: 75, engagement: 70 },
  { month: 'Feb', performance: 78, engagement: 72 },
  { month: 'Mar', performance: 82, engagement: 75 },
  { month: 'Apr', performance: 79, engagement: 73 },
  { month: 'May', performance: 85, engagement: 78 },
  { month: 'Jun', performance: 87, engagement: 82 },
];

const examTypeData = [
  { name: 'Quiz', value: 35, color: '#8884d8' },
  { name: 'CIA 1', value: 25, color: '#82ca9d' },
  { name: 'CIA 2', value: 25, color: '#ffc658' },
  { name: 'Assignment', value: 15, color: '#ff7300' },
];

const chapterAnalyticsData = [
  { chapter: 'Introduction', understanding: 90, difficulty: 20, completion: 95 },
  { chapter: 'Basic Concepts', understanding: 85, difficulty: 30, completion: 92 },
  { chapter: 'Advanced Topics', understanding: 75, difficulty: 60, completion: 88 },
  { chapter: 'Applications', understanding: 80, difficulty: 45, completion: 90 },
  { chapter: 'Case Studies', understanding: 78, difficulty: 50, completion: 85 },
];

const weakAreasData = [
  { area: 'Neural Networks - Backpropagation', course: 'Machine Learning', weakStudents: 12, percentage: 27 },
  { area: 'Dynamic Programming', course: 'Algorithms', weakStudents: 8, percentage: 22 },
  { area: 'Database Normalization', course: 'Database Systems', weakStudents: 10, percentage: 24 },
  { area: 'React State Management', course: 'Web Development', weakStudents: 6, percentage: 16 },
  { area: 'Tree Traversals', course: 'Data Structures', weakStudents: 9, percentage: 17 },
];

const Analytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [error] = useState('');

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon, 
    color 
  }: { 
    title: string; 
    value: string | number; 
    change: number; 
    icon: React.ReactNode; 
    color: string;
  }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ color, fontWeight: 'bold' }}>
              {value}
            </Typography>
            <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
              {change > 0 ? (
                <TrendingUpIcon sx={{ color: 'success.main', mr: 0.5, fontSize: 20 }} />
              ) : (
                <TrendingDownIcon sx={{ color: 'error.main', mr: 0.5, fontSize: 20 }} />
              )}
              <Typography 
                variant="body2" 
                sx={{ 
                  color: change > 0 ? 'success.main' : 'error.main',
                  fontWeight: 'medium'
                }}
              >
                {Math.abs(change)}% vs last month
              </Typography>
            </Box>
          </Box>
          <Box sx={{ color, opacity: 0.8 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Analytics Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Key Metrics */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
        <Box sx={{ flex: 1, minWidth: 250 }}>
          <StatCard
            title="Average Performance"
            value="83%"
            change={6}
            icon={<AnalyticsIcon sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Box>
        <Box sx={{ flex: 1, minWidth: 250 }}>
          <StatCard
            title="Course Completion"
            value="91%"
            change={4}
            icon={<SchoolIcon sx={{ fontSize: 40 }} />}
            color="#388e3c"
          />
        </Box>
        <Box sx={{ flex: 1, minWidth: 250 }}>
          <StatCard
            title="Student Engagement"
            value="87%"
            change={8}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="#f57c00"
          />
        </Box>
        <Box sx={{ flex: 1, minWidth: 250 }}>
          <StatCard
            title="Assessment Rate"
            value="94%"
            change={2}
            icon={<QuizIcon sx={{ fontSize: 40 }} />}
            color="#7b1fa2"
          />
        </Box>
      </Box>

      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="Performance Analytics" />
        <Tab label="Learning Insights" />
        <Tab label="Weak Areas Analysis" />
      </Tabs>

      {/* Performance Analytics Tab */}
      {tabValue === 0 && (
        <Stack spacing={3}>
          {/* Course Performance Chart */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Course-wise Performance Analysis
              </Typography>
              <Box sx={{ width: '100%', height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="course" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="avgScore" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          {/* Trend Analysis */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Card sx={{ flex: 2, minWidth: 400 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Trend (6 Months)
                </Typography>
                <Box sx={{ width: '100%', height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Area 
                        type="monotone" 
                        dataKey="performance" 
                        stroke="#8884d8" 
                        fill="#8884d8" 
                        fillOpacity={0.3}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="engagement" 
                        stroke="#82ca9d" 
                        fill="#82ca9d" 
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>

            {/* Exam Type Distribution */}
            <Card sx={{ flex: 1, minWidth: 300 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Assessment Distribution
                </Typography>
                <Box sx={{ width: '100%', height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={examTypeData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {examTypeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Stack>
      )}

      {/* Learning Insights Tab */}
      {tabValue === 1 && (
        <Stack spacing={3}>
          {/* Chapter Analytics */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Chapter-wise Learning Analytics
              </Typography>
              <Box sx={{ width: '100%', height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chapterAnalyticsData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="chapter" />
                    <PolarRadiusAxis />
                    <Radar
                      name="Understanding"
                      dataKey="understanding"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.3}
                    />
                    <Radar
                      name="Completion"
                      dataKey="completion"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      fillOpacity={0.3}
                    />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          {/* Chapter Details */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Chapter Analysis
              </Typography>
              {chapterAnalyticsData.map((chapter, index) => (
                <Box key={index} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {chapter.chapter}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                      <Typography variant="body2">Understanding Level</Typography>
                      <Typography variant="body2">{chapter.understanding}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={chapter.understanding}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          bgcolor: chapter.understanding >= 85 ? '#4caf50' : 
                                   chapter.understanding >= 70 ? '#ff9800' : '#f44336',
                        },
                      }}
                    />
                  </Box>
                  <Box display="flex" gap={2}>
                    <Chip
                      label={`Difficulty: ${chapter.difficulty}%`}
                      color={chapter.difficulty <= 30 ? 'success' : 
                             chapter.difficulty <= 50 ? 'warning' : 'error'}
                      size="small"
                    />
                    <Chip
                      label={`Completion: ${chapter.completion}%`}
                      color={chapter.completion >= 90 ? 'success' : 'info'}
                      size="small"
                    />
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Stack>
      )}

      {/* Weak Areas Analysis Tab */}
      {tabValue === 2 && (
        <Stack spacing={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Areas Needing Attention
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Identified weak areas where students need additional support
              </Typography>
              
              <List>
                {weakAreasData.map((area, index) => (
                  <ListItem key={index} sx={{ py: 2, px: 0 }}>
                    <ListItemIcon>
                      <WarningIcon 
                        color={area.percentage >= 25 ? 'error' : 'warning'} 
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={area.area}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {area.course} • {area.weakStudents} students struggling
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={area.percentage}
                              sx={{
                                flex: 1,
                                mr: 2,
                                height: 6,
                                borderRadius: 3,
                                bgcolor: 'grey.200',
                                '& .MuiLinearProgress-bar': {
                                  borderRadius: 3,
                                  bgcolor: area.percentage >= 25 ? '#f44336' : '#ff9800',
                                },
                              }}
                            />
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {area.percentage}%
                            </Typography>
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI-Powered Recommendations
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ p: 2, bgcolor: 'info.50', borderRadius: 2, border: '1px solid', borderColor: 'info.200' }}>
                  <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
                    <CheckCircleIcon sx={{ color: 'info.main', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Focus on Neural Networks
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    Consider organizing additional tutorial sessions for Neural Networks - Backpropagation. 
                    27% of students in Machine Learning are struggling with this concept.
                  </Typography>
                </Box>

                <Box sx={{ p: 2, bgcolor: 'warning.50', borderRadius: 2, border: '1px solid', borderColor: 'warning.200' }}>
                  <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
                    <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Dynamic Programming Resources
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    Provide additional practice problems and visual explanations for Dynamic Programming. 
                    Consider creating step-by-step video tutorials.
                  </Typography>
                </Box>

                <Box sx={{ p: 2, bgcolor: 'success.50', borderRadius: 2, border: '1px solid', borderColor: 'success.200' }}>
                  <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
                    <TrendingUpIcon sx={{ color: 'success.main', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Web Development Excellence
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    Web Development course is performing exceptionally well with 88% average. 
                    Consider using similar teaching methodologies for other courses.
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      )}
    </Box>
  );
};

export default Analytics;
