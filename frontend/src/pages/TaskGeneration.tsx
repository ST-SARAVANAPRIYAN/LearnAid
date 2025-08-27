import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  AutoAwesome as AIIcon,
  Quiz as QuizIcon,
  Assignment as TaskIcon,
  ExpandMore as ExpandIcon,
  Visibility as ViewIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';

import PDFUpload from '../components/PDFUpload';

interface TaskGenerationProps {}

interface GeneratedQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty: string;
  topic: string;
  quality_score: number;
}

interface TaskStats {
  total_tasks: number;
  active_tasks: number;
  total_questions: number;
  task_types: Array<{ type: string; count: number }>;
  difficulty_distribution: Array<{ level: string; count: number }>;
}

const TaskGeneration: React.FC<TaskGenerationProps> = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [viewQuestionDialog, setViewQuestionDialog] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<GeneratedQuestion | null>(null);

  // Form states
  const [questionGenForm, setQuestionGenForm] = useState({
    content: '',
    topic: '',
    num_questions: 5,
    difficulty: 'medium'
  });

  const [taskGenForm, setTaskGenForm] = useState({
    student_id: '',
    course_id: '',
    task_type: 'improvement'
  });

  // Mock data for dropdowns
  const courses = [
    { id: 1, name: 'Computer Science 101', code: 'CS101' },
    { id: 2, name: 'Data Structures', code: 'CS201' },
    { id: 3, name: 'Machine Learning', code: 'CS301' },
  ];

  const students = [
    { id: 1, name: 'Alice Johnson', email: 'alice@student.edu' },
    { id: 2, name: 'Bob Smith', email: 'bob@student.edu' },
    { id: 3, name: 'Charlie Brown', email: 'charlie@student.edu' },
  ];

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/llm/task-generation-stats');
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const generateQuestions = async () => {
    if (!questionGenForm.content.trim()) {
      alert('Please provide content for question generation');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/llm/generate-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionGenForm),
      });

      const data = await response.json();
      if (data.success) {
        setQuestions(data.questions);
        setActiveTab(3); // Switch to questions tab
      } else {
        alert('Failed to generate questions: ' + data.message);
      }
    } catch (error) {
      alert('Error generating questions: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const generatePersonalizedTask = async () => {
    if (!taskGenForm.student_id || !taskGenForm.course_id) {
      alert('Please select both student and course');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/llm/generate-personalized-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskGenForm),
      });

      const data = await response.json();
      if (data.success) {
        alert(`Task generated successfully! Task ID: ${data.task_id}, Questions: ${data.questions_generated}`);
        loadStats(); // Refresh stats
      } else {
        alert('Failed to generate task: ' + data.message);
      }
    } catch (error) {
      alert('Error generating task: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const scheduleWeeklyTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/llm/schedule-weekly-tasks', {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        alert('Weekly task scheduling initiated successfully!');
        loadStats();
      } else {
        alert('Failed to schedule tasks');
      }
    } catch (error) {
      alert('Error scheduling tasks: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const viewQuestion = (question: GeneratedQuestion) => {
    setSelectedQuestion(question);
    setViewQuestionDialog(true);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Task Generation & Content Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload PDFs, generate questions, and create personalized tasks using AI
        </Typography>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr 1fr' },
          gap: 2,
          mb: 4
        }}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TaskIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4">{stats.total_tasks}</Typography>
              <Typography variant="body2" color="text.secondary">Total Tasks</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <QuizIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4">{stats.total_questions}</Typography>
              <Typography variant="body2" color="text.secondary">Questions Generated</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AIIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4">{stats.active_tasks}</Typography>
              <Typography variant="body2" color="text.secondary">Active Tasks</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AnalyticsIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4">
                {((stats.active_tasks / Math.max(stats.total_tasks, 1)) * 100).toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">Task Completion Rate</Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Main Content Tabs */}
      <Paper>
        <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Upload PDFs" icon={<UploadIcon />} />
          <Tab label="Generate Questions" icon={<QuizIcon />} />
          <Tab label="Create Tasks" icon={<TaskIcon />} />
          <Tab label="Generated Questions" icon={<AIIcon />} />
        </Tabs>

        {/* Tab Content */}
        <Box sx={{ p: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Upload Course Chapter PDFs
              </Typography>
              <PDFUpload
                onUploadComplete={(fileInfo) => {
                  console.log('Upload completed:', fileInfo);
                  loadStats(); // Refresh stats after upload
                }}
              />
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Generate MCQ Questions from Content
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
                <Box>
                  <TextField
                    fullWidth
                    multiline
                    rows={10}
                    label="Content"
                    placeholder="Paste or type the content from which to generate questions..."
                    value={questionGenForm.content}
                    onChange={(e) => setQuestionGenForm(prev => ({ ...prev, content: e.target.value }))}
                    sx={{ mb: 3 }}
                  />
                  
                  <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                    <TextField
                      label="Topic"
                      value={questionGenForm.topic}
                      onChange={(e) => setQuestionGenForm(prev => ({ ...prev, topic: e.target.value }))}
                      sx={{ minWidth: 200 }}
                    />
                    
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>Questions</InputLabel>
                      <Select
                        value={questionGenForm.num_questions}
                        onChange={(e) => setQuestionGenForm(prev => ({ ...prev, num_questions: Number(e.target.value) }))}
                      >
                        {[3, 5, 10, 15, 20].map(num => (
                          <MenuItem key={num} value={num}>{num}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>Difficulty</InputLabel>
                      <Select
                        value={questionGenForm.difficulty}
                        onChange={(e) => setQuestionGenForm(prev => ({ ...prev, difficulty: e.target.value }))}
                      >
                        <MenuItem value="easy">Easy</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="hard">Hard</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                  
                  <Button
                    variant="contained"
                    onClick={generateQuestions}
                    disabled={loading || !questionGenForm.content.trim()}
                    startIcon={<AIIcon />}
                    size="large"
                  >
                    {loading ? 'Generating Questions...' : 'Generate Questions'}
                  </Button>
                </Box>
                
                <Box>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Tips for Better Questions</Typography>
                      <List dense>
                        <ListItem>
                          <ListItemText primary="Provide clear, well-structured content" />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Include key concepts and definitions" />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Specify the topic for context" />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Choose appropriate difficulty level" />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Box>
              </Box>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Create Personalized Tasks
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                <Box>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Individual Task Generation</Typography>
                      
                      <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Student</InputLabel>
                        <Select
                          value={taskGenForm.student_id}
                          onChange={(e) => setTaskGenForm(prev => ({ ...prev, student_id: e.target.value }))}
                        >
                          {students.map(student => (
                            <MenuItem key={student.id} value={student.id.toString()}>
                              {student.name} ({student.email})
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      
                      <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Course</InputLabel>
                        <Select
                          value={taskGenForm.course_id}
                          onChange={(e) => setTaskGenForm(prev => ({ ...prev, course_id: e.target.value }))}
                        >
                          {courses.map(course => (
                            <MenuItem key={course.id} value={course.id.toString()}>
                              {course.code} - {course.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      
                      <FormControl fullWidth sx={{ mb: 3 }}>
                        <InputLabel>Task Type</InputLabel>
                        <Select
                          value={taskGenForm.task_type}
                          onChange={(e) => setTaskGenForm(prev => ({ ...prev, task_type: e.target.value }))}
                        >
                          <MenuItem value="improvement">Improvement (Weak Areas)</MenuItem>
                          <MenuItem value="reinforcement">Reinforcement (Strong Areas)</MenuItem>
                          <MenuItem value="challenge">Challenge (Advanced)</MenuItem>
                        </Select>
                      </FormControl>
                      
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={generatePersonalizedTask}
                        disabled={loading}
                        startIcon={<TaskIcon />}
                      >
                        Generate Personalized Task
                      </Button>
                    </CardContent>
                  </Card>
                </Box>
                
                <Box>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Bulk Operations</Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Generate tasks for multiple students at once
                      </Typography>
                      
                      <Button
                        fullWidth
                        variant="outlined"
                        onClick={scheduleWeeklyTasks}
                        disabled={loading}
                        startIcon={<AnalyticsIcon />}
                        sx={{ mb: 2 }}
                      >
                        Schedule Weekly Tasks for All Students
                      </Button>
                      
                      <Alert severity="info" sx={{ mt: 2 }}>
                        Weekly scheduling will analyze all student performances and create personalized improvement tasks.
                      </Alert>
                    </CardContent>
                  </Card>
                </Box>
              </Box>
            </Box>
          )}

          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Generated Questions ({questions.length})
              </Typography>
              
              {questions.length === 0 ? (
                <Alert severity="info">
                  No questions generated yet. Use the "Generate Questions" tab to create some.
                </Alert>
              ) : (
                <Box>
                  {questions.map((question, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <Typography variant="body1" sx={{ flexGrow: 1 }}>
                            Question {index + 1}: {question.question.substring(0, 80)}...
                          </Typography>
                          <Chip 
                            label={question.difficulty} 
                            size="small" 
                            color={
                              question.difficulty === 'easy' ? 'success' :
                              question.difficulty === 'medium' ? 'primary' : 'warning'
                            }
                          />
                          <Chip 
                            label={`${(question.quality_score * 100).toFixed(0)}%`}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>Question:</Typography>
                          <Typography variant="body2" sx={{ mb: 2 }}>{question.question}</Typography>
                          
                          <Typography variant="subtitle2" gutterBottom>Options:</Typography>
                          {question.options.map((option, optIndex) => (
                            <Typography 
                              key={optIndex} 
                              variant="body2" 
                              sx={{ 
                                mb: 0.5,
                                fontWeight: optIndex === question.correct_answer ? 'bold' : 'normal',
                                color: optIndex === question.correct_answer ? 'success.main' : 'text.primary'
                              }}
                            >
                              {String.fromCharCode(65 + optIndex)}) {option}
                              {optIndex === question.correct_answer && ' ✓'}
                            </Typography>
                          ))}
                          
                          <Typography variant="subtitle2" sx={{ mt: 2 }} gutterBottom>Explanation:</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {question.explanation}
                          </Typography>
                          
                          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                            <Button 
                              size="small" 
                              variant="outlined" 
                              startIcon={<ViewIcon />}
                              onClick={() => viewQuestion(question)}
                            >
                              Preview
                            </Button>
                          </Box>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Box>
      </Paper>

      {/* Loading Progress */}
      {loading && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Question Preview Dialog */}
      <Dialog 
        open={viewQuestionDialog} 
        onClose={() => setViewQuestionDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Question Preview</DialogTitle>
        <DialogContent>
          {selectedQuestion && (
            <Box sx={{ py: 2 }}>
              <Typography variant="h6" gutterBottom>{selectedQuestion.question}</Typography>
              
              {selectedQuestion.options.map((option, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    p: 1,
                    mb: 1,
                    borderRadius: 1,
                    backgroundColor: index === selectedQuestion.correct_answer ? 'success.light' : 'grey.100',
                    border: index === selectedQuestion.correct_answer ? '2px solid green' : '1px solid grey'
                  }}
                >
                  <Typography variant="body1">
                    {String.fromCharCode(65 + index)}) {option}
                  </Typography>
                </Box>
              ))}
              
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Explanation:</strong> {selectedQuestion.explanation}
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewQuestionDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskGeneration;
