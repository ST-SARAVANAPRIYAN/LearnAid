import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Radio,
  RadioGroup,
  FormControl,
  FormControlLabel,
  Paper,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Timer,
  Warning,
  CheckCircle,
  Cancel,
  PlayArrow,
  Stop,
  NavigateNext,
  NavigateBefore,
  Flag,
  School,
  Assignment,
} from '@mui/icons-material';

interface MCQOption {
  option_id: string;
  option_text: string;
  is_correct?: boolean; // Only available after submission
}

interface MCQQuestion {
  question_id: number;
  question_text: string;
  options: MCQOption[];
  explanation?: string; // Only available after submission
  difficulty: string;
  chapter_reference?: string;
}

interface TaskInfo {
  assignment_id: number;
  task_id: number;
  task_title: string;
  course_name: string;
  chapter_title: string;
  task_type: string;
  difficulty: string;
  time_limit: number; // in minutes
  total_questions: number;
  passing_score: number;
  max_attempts: number;
  current_attempt: number;
}

interface TestResult {
  score: number;
  total_questions: number;
  percentage: number;
  passed: boolean;
  time_taken: number;
  correct_answers: number;
  incorrect_answers: number;
  skipped_questions: number;
}

interface UserAnswer {
  question_id: number;
  selected_option: string;
  is_flagged: boolean;
}

const MCQTestComponent: React.FC<{ assignmentId: number; onComplete: () => void }> = ({
  assignmentId,
  onComplete,
}) => {
  const [taskInfo, setTaskInfo] = useState<TaskInfo | null>(null);
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Map<number, UserAnswer>>(new Map());
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<number>>(new Set());
  const [timeRemaining, setTimeRemaining] = useState(0); // in seconds
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitDialogOpen, setSubmitDialogOpen] = useState(false);
  const [autoSubmit, setAutoSubmit] = useState(false);

  // Mock data for development
  const mockTaskInfo: TaskInfo = {
    assignment_id: assignmentId,
    task_id: 1,
    task_title: 'Arrays and Linked Lists Practice',
    course_name: 'Data Structures and Algorithms',
    chapter_title: 'Arrays and Linked Lists',
    task_type: 'frequent_assessment',
    difficulty: 'medium',
    time_limit: 20,
    total_questions: 10,
    passing_score: 60,
    max_attempts: 3,
    current_attempt: 1,
  };

  const mockQuestions: MCQQuestion[] = [
    {
      question_id: 1,
      question_text: 'What is the time complexity of accessing an element in an array by index?',
      options: [
        { option_id: 'A', option_text: 'O(1)' },
        { option_id: 'B', option_text: 'O(log n)' },
        { option_id: 'C', option_text: 'O(n)' },
        { option_id: 'D', option_text: 'O(n²)' },
      ],
      difficulty: 'easy',
      chapter_reference: 'Array Basics',
    },
    {
      question_id: 2,
      question_text: 'Which operation is more efficient in a linked list compared to an array?',
      options: [
        { option_id: 'A', option_text: 'Random access' },
        { option_id: 'B', option_text: 'Insertion at the beginning' },
        { option_id: 'C', option_text: 'Memory usage' },
        { option_id: 'D', option_text: 'Cache performance' },
      ],
      difficulty: 'medium',
      chapter_reference: 'Linked Lists vs Arrays',
    },
    {
      question_id: 3,
      question_text: 'What happens when you try to access an array element beyond its bounds in most programming languages?',
      options: [
        { option_id: 'A', option_text: 'Returns null' },
        { option_id: 'B', option_text: 'Returns 0' },
        { option_id: 'C', option_text: 'Throws an exception or undefined behavior' },
        { option_id: 'D', option_text: 'Creates a new element' },
      ],
      difficulty: 'easy',
      chapter_reference: 'Array Safety',
    },
    {
      question_id: 4,
      question_text: 'In a singly linked list, which pointer/reference is typically stored in each node?',
      options: [
        { option_id: 'A', option_text: 'Pointer to the previous node only' },
        { option_id: 'B', option_text: 'Pointer to the next node only' },
        { option_id: 'C', option_text: 'Pointers to both previous and next nodes' },
        { option_id: 'D', option_text: 'Pointer to the head node' },
      ],
      difficulty: 'easy',
      chapter_reference: 'Linked List Structure',
    },
    {
      question_id: 5,
      question_text: 'What is the space complexity of an array of size n?',
      options: [
        { option_id: 'A', option_text: 'O(1)' },
        { option_id: 'B', option_text: 'O(log n)' },
        { option_id: 'C', option_text: 'O(n)' },
        { option_id: 'D', option_text: 'O(n²)' },
      ],
      difficulty: 'easy',
      chapter_reference: 'Space Complexity',
    },
  ];

  // Initialize test data
  useEffect(() => {
    const initializeTest = async () => {
      setLoading(true);
      try {
        // Simulate API call to fetch task info and questions
        await new Promise(resolve => setTimeout(resolve, 1000));
        setTaskInfo(mockTaskInfo);
        setQuestions(mockQuestions);
        setTimeRemaining(mockTaskInfo.time_limit * 60); // Convert minutes to seconds
      } catch (error) {
        console.error('Error initializing test:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeTest();
  }, [assignmentId]);

  // Timer logic
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;

    if (testStarted && !testCompleted && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            setAutoSubmit(true);
            handleSubmitTest(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [testStarted, testCompleted, timeRemaining]);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getTimerColor = (seconds: number): 'error' | 'warning' | 'primary' => {
    const percentage = (seconds / (taskInfo!.time_limit * 60)) * 100;
    if (percentage <= 10) return 'error';
    if (percentage <= 25) return 'warning';
    return 'primary';
  };

  const handleStartTest = () => {
    setTestStarted(true);
  };

  const handleAnswerChange = (questionId: number, selectedOption: string) => {
    setUserAnswers(prev => {
      const newAnswers = new Map(prev);
      newAnswers.set(questionId, {
        question_id: questionId,
        selected_option: selectedOption,
        is_flagged: flaggedQuestions.has(questionId),
      });
      return newAnswers;
    });
  };

  const handleFlagQuestion = (questionId: number) => {
    setFlaggedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });

    // Update answer with flag status
    setUserAnswers(prev => {
      const newAnswers = new Map(prev);
      const existingAnswer = newAnswers.get(questionId);
      if (existingAnswer) {
        newAnswers.set(questionId, {
          ...existingAnswer,
          is_flagged: !flaggedQuestions.has(questionId),
        });
      }
      return newAnswers;
    });
  };

  const handleSubmitTest = useCallback(async (isAutoSubmit = false) => {
    if (!isAutoSubmit) {
      setSubmitDialogOpen(false);
    }

    setTestCompleted(true);

    try {
      // Calculate results
      const answeredQuestions = userAnswers.size;
      const skippedQuestions = questions.length - answeredQuestions;
      
      // Mock scoring (in real app, this would be done on the server)
      const correctAnswers = Math.floor(Math.random() * answeredQuestions * 0.8) + Math.floor(answeredQuestions * 0.2);
      const incorrectAnswers = answeredQuestions - correctAnswers;
      const score = Math.round((correctAnswers / questions.length) * 100);
      
      const result: TestResult = {
        score,
        total_questions: questions.length,
        percentage: score,
        passed: score >= taskInfo!.passing_score,
        time_taken: (taskInfo!.time_limit * 60) - timeRemaining,
        correct_answers: correctAnswers,
        incorrect_answers: incorrectAnswers,
        skipped_questions: skippedQuestions,
      };

      setTestResult(result);

      // Simulate API call to submit results
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {
      console.error('Error submitting test:', error);
    }
  }, [userAnswers, questions.length, taskInfo, timeRemaining]);

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const goToQuestion = (index: number) => {
    setCurrentQuestionIndex(index);
  };

  const getQuestionStatus = (index: number): 'answered' | 'flagged' | 'unanswered' => {
    const questionId = questions[index]?.question_id;
    if (flaggedQuestions.has(questionId)) return 'flagged';
    if (userAnswers.has(questionId)) return 'answered';
    return 'unanswered';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!taskInfo || questions.length === 0) {
    return (
      <Alert severity="error">
        Failed to load test data. Please try again.
      </Alert>
    );
  }

  // Test completion screen
  if (testCompleted && testResult) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            {autoSubmit && (
              <Alert severity="warning" sx={{ mb: 3 }}>
                <Timer /> Test was automatically submitted due to time expiration.
              </Alert>
            )}
            
            <Box sx={{ mb: 3 }}>
              {testResult.passed ? (
                <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              ) : (
                <Cancel sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
              )}
            </Box>

            <Typography variant="h4" sx={{ fontWeight: 600, mb: 2 }}>
              {testResult.passed ? 'Congratulations! 🎉' : 'Better luck next time! 💪'}
            </Typography>

            <Typography variant="h5" color={testResult.passed ? 'success.main' : 'error.main'} sx={{ mb: 3 }}>
              Score: {testResult.score}% ({testResult.correct_answers}/{testResult.total_questions})
            </Typography>

            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr 1fr' },
              gap: 3,
              mb: 4,
              maxWidth: 600,
              mx: 'auto'
            }}>
              <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="success.main" sx={{ fontWeight: 600 }}>
                  {testResult.correct_answers}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Correct
                </Typography>
              </Paper>
              
              <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="error.main" sx={{ fontWeight: 600 }}>
                  {testResult.incorrect_answers}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Incorrect
                </Typography>
              </Paper>
              
              <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="warning.main" sx={{ fontWeight: 600 }}>
                  {testResult.skipped_questions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Skipped
                </Typography>
              </Paper>
            </Box>

            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Time taken: {formatTime(testResult.time_taken)}
            </Typography>

            {!testResult.passed && taskInfo.current_attempt < taskInfo.max_attempts && (
              <Alert severity="info" sx={{ mb: 3 }}>
                You can attempt this test {taskInfo.max_attempts - taskInfo.current_attempt} more time(s).
                Consider reviewing the chapter material before retrying.
              </Alert>
            )}

            <Button
              variant="contained"
              size="large"
              onClick={onComplete}
              sx={{ minWidth: 200 }}
            >
              Continue to Dashboard
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Pre-test screen
  if (!testStarted) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Assignment color="primary" />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {taskInfo.task_title}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <School color="action" />
              <Typography variant="body1" color="text.secondary">
                {taskInfo.course_name} • {taskInfo.chapter_title}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
              <Chip
                label={`${taskInfo.total_questions} Questions`}
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`${taskInfo.time_limit} Minutes`}
                color="warning"
                variant="outlined"
                icon={<Timer />}
              />
              <Chip
                label={`Pass: ${taskInfo.passing_score}%`}
                color="success"
                variant="outlined"
              />
              <Chip
                label={`Attempt ${taskInfo.current_attempt}/${taskInfo.max_attempts}`}
                color="info"
                variant="outlined"
              />
            </Box>
          </Box>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Important Instructions:
            </Typography>
            <Box component="ul" sx={{ pl: 2, m: 0 }}>
              <li>You have {taskInfo.time_limit} minutes to complete {taskInfo.total_questions} questions</li>
              <li>You need at least {taskInfo.passing_score}% to pass this assessment</li>
              <li>You can flag questions for review and navigate between questions</li>
              <li>The test will auto-submit when time expires</li>
              <li>Make sure you have a stable internet connection</li>
            </Box>
          </Alert>

          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleStartTest}
              sx={{ minWidth: 200 }}
            >
              Start Test
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Test in progress
  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <Box sx={{ maxWidth: '100%', mx: 'auto' }}>
      {/* Timer and Progress Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Timer color={getTimerColor(timeRemaining)} />
              <Typography variant="h6" color={getTimerColor(timeRemaining) + '.main'} sx={{ fontWeight: 600 }}>
                {formatTime(timeRemaining)}
              </Typography>
            </Box>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Stop />}
              onClick={() => setSubmitDialogOpen(true)}
            >
              Submit Test
            </Button>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Question {currentQuestionIndex + 1} of {questions.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {progress.toFixed(0)}% Complete
            </Typography>
          </Box>
          
          <LinearProgress variant="determinate" value={progress} sx={{ height: 6, borderRadius: 3 }} />
        </CardContent>
      </Card>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 300px' }, gap: 3 }}>
        {/* Question Panel */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Question {currentQuestionIndex + 1}
                </Typography>
                <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                  {currentQuestion.question_text}
                </Typography>
              </Box>
              <Tooltip title={flaggedQuestions.has(currentQuestion.question_id) ? 'Unflag Question' : 'Flag for Review'}>
                <IconButton
                  onClick={() => handleFlagQuestion(currentQuestion.question_id)}
                  color={flaggedQuestions.has(currentQuestion.question_id) ? 'warning' : 'default'}
                >
                  <Flag />
                </IconButton>
              </Tooltip>
            </Box>

            <FormControl component="fieldset" sx={{ width: '100%' }}>
              <RadioGroup
                value={userAnswers.get(currentQuestion.question_id)?.selected_option || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.question_id, e.target.value)}
              >
                {currentQuestion.options.map((option) => (
                  <FormControlLabel
                    key={option.option_id}
                    value={option.option_id}
                    control={<Radio />}
                    label={`${option.option_id}. ${option.option_text}`}
                    sx={{ 
                      mb: 2, 
                      p: 2, 
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      '&:hover': { 
                        backgroundColor: 'action.hover' 
                      }
                    }}
                  />
                ))}
              </RadioGroup>
            </FormControl>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4 }}>
              <Button
                startIcon={<NavigateBefore />}
                onClick={handlePreviousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              
              <Typography variant="body2" color="text.secondary">
                {userAnswers.size} of {questions.length} answered
              </Typography>
              
              <Button
                endIcon={<NavigateNext />}
                onClick={handleNextQuestion}
                disabled={currentQuestionIndex === questions.length - 1}
              >
                Next
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Question Navigator Panel */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Question Navigator
            </Typography>
            
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(5, 1fr)',
              gap: 1,
              mb: 3
            }}>
              {questions.map((_, index) => {
                const status = getQuestionStatus(index);
                const isActive = index === currentQuestionIndex;
                
                return (
                  <Button
                    key={index}
                    variant={isActive ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => goToQuestion(index)}
                    sx={{
                      minWidth: 40,
                      height: 40,
                      borderColor: status === 'answered' ? 'success.main' : 
                                  status === 'flagged' ? 'warning.main' : 'divider',
                      backgroundColor: isActive ? 'primary.main' : 
                                     status === 'answered' ? 'success.light' :
                                     status === 'flagged' ? 'warning.light' : 'transparent',
                      color: isActive ? 'primary.contrastText' :
                            status === 'answered' ? 'success.main' :
                            status === 'flagged' ? 'warning.main' : 'text.primary',
                      '&:hover': {
                        backgroundColor: isActive ? 'primary.dark' : 'action.hover',
                      },
                    }}
                  >
                    {index + 1}
                  </Button>
                );
              })}
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box sx={{ width: 12, height: 12, bgcolor: 'success.light', borderRadius: 1 }} />
                <Typography variant="caption">Answered ({userAnswers.size})</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box sx={{ width: 12, height: 12, bgcolor: 'warning.light', borderRadius: 1 }} />
                <Typography variant="caption">Flagged ({flaggedQuestions.size})</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 12, height: 12, bgcolor: 'grey.200', borderRadius: 1 }} />
                <Typography variant="caption">Unanswered ({questions.length - userAnswers.size})</Typography>
              </Box>
            </Box>

            <Button
              variant="contained"
              color="success"
              fullWidth
              onClick={() => setSubmitDialogOpen(true)}
              disabled={userAnswers.size === 0}
            >
              Submit Test
            </Button>
          </CardContent>
        </Card>
      </Box>

      {/* Submit Confirmation Dialog */}
      <Dialog open={submitDialogOpen} onClose={() => setSubmitDialogOpen(false)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Warning color="warning" />
            Confirm Test Submission
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to submit your test? This action cannot be undone.
          </Typography>
          <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Summary:</strong>
            </Typography>
            <Typography variant="body2">
              • Answered: {userAnswers.size} of {questions.length} questions
            </Typography>
            <Typography variant="body2">
              • Flagged: {flaggedQuestions.size} questions
            </Typography>
            <Typography variant="body2">
              • Time remaining: {formatTime(timeRemaining)}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubmitDialogOpen(false)}>
            Continue Test
          </Button>
          <Button onClick={() => handleSubmitTest(false)} variant="contained" color="primary">
            Submit Test
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MCQTestComponent;
