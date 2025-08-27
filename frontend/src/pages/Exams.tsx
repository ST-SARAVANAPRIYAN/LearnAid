import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Quiz as QuizIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { facultyService } from '../services/api';

interface Course {
  id: number;
  name: string;
  code: string;
}

interface Exam {
  id: number;
  title: string;
  course_id: number;
  course_name: string;
  exam_type: 'quiz' | 'cia1' | 'cia2' | 'semester';
  total_marks: number;
  duration_minutes: number;
  exam_date: string;
  status: 'draft' | 'published' | 'completed';
  questions_count?: number;
}

interface Question {
  id: number;
  exam_id: number;
  question_text: string;
  question_type: 'mcq' | 'descriptive' | 'fill_blank';
  marks: number;
  chapter: string;
  options?: string[];
  correct_answer?: string;
}

const Exams: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [exams, setExams] = useState<Exam[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Dialog states
  const [examDialogOpen, setExamDialogOpen] = useState(false);
  const [questionDialogOpen, setQuestionDialogOpen] = useState(false);
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null);
  const [editingExam, setEditingExam] = useState<Exam | null>(null);
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);

  // Form states
  const [examFormData, setExamFormData] = useState({
    title: '',
    course_id: '',
    exam_type: 'quiz',
    total_marks: 100,
    duration_minutes: 60,
    exam_date: '',
  });

  const [questionFormData, setQuestionFormData] = useState({
    question_text: '',
    question_type: 'mcq',
    marks: 1,
    chapter: '',
    options: ['', '', '', ''],
    correct_answer: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [examsResponse, coursesResponse] = await Promise.all([
        facultyService.getExams(),
        facultyService.getCourses(),
      ]);
      setExams(examsResponse.data);
      setCourses(coursesResponse.data);
    } catch (err: any) {
      setError('Failed to fetch data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestions = async (examId: number) => {
    try {
      const response = await facultyService.getExamQuestions(examId);
      setQuestions(response.data);
    } catch (err: any) {
      console.error('Questions fetch error:', err);
    }
  };

  const handleExamSubmit = async () => {
    try {
      if (editingExam) {
        await facultyService.updateExam(editingExam.id, examFormData);
      } else {
        await facultyService.createExam(examFormData);
      }
      await fetchData();
      setExamDialogOpen(false);
      resetExamForm();
    } catch (err: any) {
      setError(editingExam ? 'Failed to update exam' : 'Failed to create exam');
    }
  };

  const handleQuestionSubmit = async () => {
    if (!selectedExam) return;
    
    try {
      const questionData = {
        ...questionFormData,
        exam_id: selectedExam.id,
        options: questionFormData.question_type === 'mcq' ? questionFormData.options : undefined,
      };
      
      if (editingQuestion) {
        await facultyService.updateQuestion(editingQuestion.id, questionData);
      } else {
        await facultyService.createQuestion(questionData);
      }
      
      await fetchQuestions(selectedExam.id);
      setQuestionDialogOpen(false);
      resetQuestionForm();
    } catch (err: any) {
      setError(editingQuestion ? 'Failed to update question' : 'Failed to create question');
    }
  };

  const handleDeleteExam = async (examId: number) => {
    if (window.confirm('Are you sure you want to delete this exam?')) {
      try {
        await facultyService.deleteExam(examId);
        await fetchData();
      } catch (err: any) {
        setError('Failed to delete exam');
      }
    }
  };

  const handleDeleteQuestion = async (questionId: number) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      try {
        await facultyService.deleteQuestion(questionId);
        if (selectedExam) {
          await fetchQuestions(selectedExam.id);
        }
      } catch (err: any) {
        setError('Failed to delete question');
      }
    }
  };

  const resetExamForm = () => {
    setExamFormData({
      title: '',
      course_id: '',
      exam_type: 'quiz',
      total_marks: 100,
      duration_minutes: 60,
      exam_date: '',
    });
    setEditingExam(null);
  };

  const resetQuestionForm = () => {
    setQuestionFormData({
      question_text: '',
      question_type: 'mcq',
      marks: 1,
      chapter: '',
      options: ['', '', '', ''],
      correct_answer: '',
    });
    setEditingQuestion(null);
  };

  const openExamDialog = (exam?: Exam) => {
    if (exam) {
      setEditingExam(exam);
      setExamFormData({
        title: exam.title,
        course_id: exam.course_id.toString(),
        exam_type: exam.exam_type,
        total_marks: exam.total_marks,
        duration_minutes: exam.duration_minutes,
        exam_date: exam.exam_date.split('T')[0],
      });
    } else {
      resetExamForm();
    }
    setExamDialogOpen(true);
  };

  const openQuestionDialog = (question?: Question) => {
    if (question) {
      setEditingQuestion(question);
      setQuestionFormData({
        question_text: question.question_text,
        question_type: question.question_type,
        marks: question.marks,
        chapter: question.chapter,
        options: question.options || ['', '', '', ''],
        correct_answer: question.correct_answer || '',
      });
    } else {
      resetQuestionForm();
    }
    setQuestionDialogOpen(true);
  };

  const openQuestionsTab = (exam: Exam) => {
    setSelectedExam(exam);
    fetchQuestions(exam.id);
    setTabValue(1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'default';
      case 'published': return 'primary';
      case 'completed': return 'success';
      default: return 'default';
    }
  };

  const getExamTypeLabel = (type: string) => {
    switch (type) {
      case 'quiz': return 'Quiz';
      case 'cia1': return 'CIA 1';
      case 'cia2': return 'CIA 2';
      case 'semester': return 'Semester';
      default: return type;
    }
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
        Exam Management
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab 
          label="All Exams" 
          icon={<AssessmentIcon />} 
          iconPosition="start"
        />
        <Tab 
          label={selectedExam ? `Questions - ${selectedExam.title}` : 'Questions'} 
          icon={<QuizIcon />} 
          iconPosition="start"
          disabled={!selectedExam}
        />
      </Tabs>

      {/* Exams Tab */}
      {tabValue === 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Exams List</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => openExamDialog()}
              >
                Create New Exam
              </Button>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Title</TableCell>
                    <TableCell>Course</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Marks</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {exams.map((exam) => (
                    <TableRow key={exam.id}>
                      <TableCell>{exam.title}</TableCell>
                      <TableCell>{exam.course_name}</TableCell>
                      <TableCell>
                        <Chip 
                          label={getExamTypeLabel(exam.exam_type)} 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{new Date(exam.exam_date).toLocaleDateString()}</TableCell>
                      <TableCell>{exam.duration_minutes} min</TableCell>
                      <TableCell>{exam.total_marks}</TableCell>
                      <TableCell>
                        <Chip 
                          label={exam.status} 
                          size="small" 
                          color={getStatusColor(exam.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton 
                          size="small" 
                          onClick={() => openQuestionsTab(exam)}
                          title="View Questions"
                        >
                          <QuizIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={() => openExamDialog(exam)}
                          title="Edit Exam"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteExam(exam.id)}
                          title="Delete Exam"
                          color="error"
                        >
                          <DeleteIcon />
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

      {/* Questions Tab */}
      {tabValue === 1 && selectedExam && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Box>
                <Typography variant="h6">{selectedExam.title} - Questions</Typography>
                <Typography variant="body2" color="textSecondary">
                  {selectedExam.course_name} • {questions.length} questions
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => openQuestionDialog()}
              >
                Add Question
              </Button>
            </Box>

            <List>
              {questions.map((question, index) => (
                <React.Fragment key={question.id}>
                  <ListItem>
                    <ListItemText
                      primary={`Q${index + 1}. ${question.question_text}`}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            Type: {question.question_type.toUpperCase()} • 
                            Marks: {question.marks} • 
                            Chapter: {question.chapter}
                          </Typography>
                          {question.options && (
                            <Box sx={{ mt: 1 }}>
                              {question.options.map((option, idx) => (
                                <Typography 
                                  key={idx} 
                                  variant="caption" 
                                  display="block"
                                  sx={{ 
                                    color: option === question.correct_answer ? 'success.main' : 'text.secondary',
                                    fontWeight: option === question.correct_answer ? 'bold' : 'normal'
                                  }}
                                >
                                  {String.fromCharCode(65 + idx)}. {option}
                                </Typography>
                              ))}
                            </Box>
                          )}
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        size="small" 
                        onClick={() => openQuestionDialog(question)}
                        title="Edit Question"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDeleteQuestion(question.id)}
                        title="Delete Question"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < questions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>

            {questions.length === 0 && (
              <Box textAlign="center" py={4}>
                <QuizIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                <Typography variant="body1" color="textSecondary">
                  No questions added yet. Click "Add Question" to get started.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Exam Dialog */}
      <Dialog open={examDialogOpen} onClose={() => setExamDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingExam ? 'Edit Exam' : 'Create New Exam'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Exam Title"
              value={examFormData.title}
              onChange={(e) => setExamFormData({ ...examFormData, title: e.target.value })}
            />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                select
                label="Course"
                value={examFormData.course_id}
                onChange={(e) => setExamFormData({ ...examFormData, course_id: e.target.value })}
              >
                {courses.map((course) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.code} - {course.name}
                  </MenuItem>
                ))}
              </TextField>
              
              <TextField
                fullWidth
                select
                label="Exam Type"
                value={examFormData.exam_type}
                onChange={(e) => setExamFormData({ ...examFormData, exam_type: e.target.value })}
              >
                <MenuItem value="quiz">Quiz</MenuItem>
                <MenuItem value="cia1">CIA 1</MenuItem>
                <MenuItem value="cia2">CIA 2</MenuItem>
                <MenuItem value="semester">Semester</MenuItem>
              </TextField>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                type="number"
                label="Total Marks"
                value={examFormData.total_marks}
                onChange={(e) => setExamFormData({ ...examFormData, total_marks: parseInt(e.target.value) })}
              />
              
              <TextField
                fullWidth
                type="number"
                label="Duration (minutes)"
                value={examFormData.duration_minutes}
                onChange={(e) => setExamFormData({ ...examFormData, duration_minutes: parseInt(e.target.value) })}
              />
              
              <TextField
                fullWidth
                type="date"
                label="Exam Date"
                value={examFormData.exam_date}
                onChange={(e) => setExamFormData({ ...examFormData, exam_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExamDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExamSubmit} variant="contained">
            {editingExam ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Question Dialog */}
      <Dialog open={questionDialogOpen} onClose={() => setQuestionDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingQuestion ? 'Edit Question' : 'Add New Question'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Question Text"
              value={questionFormData.question_text}
              onChange={(e) => setQuestionFormData({ ...questionFormData, question_text: e.target.value })}
            />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                select
                label="Question Type"
                value={questionFormData.question_type}
                onChange={(e) => setQuestionFormData({ ...questionFormData, question_type: e.target.value })}
              >
                <MenuItem value="mcq">Multiple Choice</MenuItem>
                <MenuItem value="descriptive">Descriptive</MenuItem>
                <MenuItem value="fill_blank">Fill in the Blank</MenuItem>
              </TextField>
              
              <TextField
                fullWidth
                type="number"
                label="Marks"
                value={questionFormData.marks}
                onChange={(e) => setQuestionFormData({ ...questionFormData, marks: parseInt(e.target.value) })}
              />
              
              <TextField
                fullWidth
                label="Chapter"
                value={questionFormData.chapter}
                onChange={(e) => setQuestionFormData({ ...questionFormData, chapter: e.target.value })}
              />
            </Box>
            
            {questionFormData.question_type === 'mcq' && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>Multiple Choice Options</Typography>
                {questionFormData.options.map((option, index) => (
                  <TextField
                    key={index}
                    fullWidth
                    label={`Option ${String.fromCharCode(65 + index)}`}
                    value={option}
                    onChange={(e) => {
                      const newOptions = [...questionFormData.options];
                      newOptions[index] = e.target.value;
                      setQuestionFormData({ ...questionFormData, options: newOptions });
                    }}
                    sx={{ mb: 1 }}
                  />
                ))}
                
                <TextField
                  fullWidth
                  select
                  label="Correct Answer"
                  value={questionFormData.correct_answer}
                  onChange={(e) => setQuestionFormData({ ...questionFormData, correct_answer: e.target.value })}
                  sx={{ mt: 2 }}
                >
                  {questionFormData.options.map((option, index) => (
                    <MenuItem key={index} value={option} disabled={!option}>
                      {String.fromCharCode(65 + index)}. {option || 'Enter option text'}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>
            )}
            
            {questionFormData.question_type !== 'mcq' && (
              <TextField
                fullWidth
                label="Model Answer / Correct Answer"
                value={questionFormData.correct_answer}
                onChange={(e) => setQuestionFormData({ ...questionFormData, correct_answer: e.target.value })}
                multiline
                rows={2}
              />
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuestionDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleQuestionSubmit} variant="contained">
            {editingQuestion ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Exams;
