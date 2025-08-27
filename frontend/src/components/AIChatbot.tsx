import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Chip,
  Divider,
  Card,
  CardContent,
  LinearProgress,
  Collapse,
  Alert,
  Fab,
  Zoom,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Close as CloseIcon,
  Chat as ChatIcon,
  Source as SourceIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const ChatContainer = styled(Box)(({ theme }) => ({
  position: 'fixed',
  bottom: 20,
  right: 20,
  width: 400,
  height: 600,
  zIndex: 1000,
  [theme.breakpoints.down('sm')]: {
    width: '90vw',
    height: '70vh',
    bottom: 10,
    right: '5vw',
  },
}));

const ChatPaper = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  boxShadow: theme.shadows[10],
}));

const ChatHeader = styled(Box)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  color: 'white',
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const MessagesContainer = styled(Box)({
  flex: 1,
  overflow: 'auto',
  padding: '16px',
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
});

const MessageBubble = styled(Box)<{ isUser: boolean }>(({ theme, isUser }) => ({
  display: 'flex',
  alignItems: 'flex-start',
  gap: theme.spacing(1),
  flexDirection: isUser ? 'row-reverse' : 'row',
}));

const BubbleContent = styled(Paper)<{ isUser: boolean }>(({ theme, isUser }) => ({
  padding: theme.spacing(1.5, 2),
  maxWidth: '80%',
  borderRadius: theme.spacing(2),
  backgroundColor: isUser ? theme.palette.primary.main : theme.palette.grey[100],
  color: isUser ? 'white' : theme.palette.text.primary,
  ...(isUser && {
    marginLeft: 'auto',
  }),
}));

const InputContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

const SourceCard = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(1),
  backgroundColor: theme.palette.background.default,
}));

const FloatingChatButton = styled(Fab)(({ theme }) => ({
  position: 'fixed',
  bottom: 20,
  right: 20,
  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  color: 'white',
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  sources?: Array<{
    content: string;
    score: number;
    source_file: string;
    chapter_name: string;
    course_id: number;
  }>;
  confidence?: number;
  processing_time?: number;
}

interface AIChatbotProps {
  studentId: number;
  courseId?: number;
}

const AIChatbot: React.FC<AIChatbotProps> = ({ studentId, courseId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<{ [key: string]: boolean }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startChatSession = async () => {
    try {
      const response = await fetch('/api/v1/chatbot/start-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          course_id: courseId,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setSessionId(data.session_id);
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          id: 'welcome',
          content: `Hello! I'm your AI learning assistant. I can help you with questions about your course materials. Feel free to ask me anything about the topics you're studying!`,
          role: 'assistant',
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Failed to start chat session:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chatbot/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          course_id: courseId,
        }),
      });

      const data = await response.json();
      
      const aiMessage: ChatMessage = {
        id: data.session_id + '_' + Date.now(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        sources: data.sources,
        confidence: data.confidence,
        processing_time: data.processing_time,
      };

      setMessages(prev => [...prev, aiMessage]);
      if (!sessionId) {
        setSessionId(data.session_id);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: 'error_' + Date.now(),
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const toggleSourceExpansion = (messageId: string) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId],
    }));
  };

  const openChat = () => {
    setIsOpen(true);
    if (!sessionId) {
      startChatSession();
    }
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';
    
    return (
      <MessageBubble key={message.id} isUser={isUser}>
        <Avatar
          sx={{ 
            bgcolor: isUser ? 'primary.main' : 'secondary.main',
            width: 32,
            height: 32,
          }}
        >
          {isUser ? <PersonIcon /> : <BotIcon />}
        </Avatar>
        
        <Box sx={{ flex: 1 }}>
          <BubbleContent isUser={isUser}>
            <Typography variant="body2">
              {message.content}
            </Typography>
            
            {message.confidence && !isUser && (
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`${Math.round(message.confidence * 100)}% confident`}
                  size="small"
                  color={message.confidence > 0.7 ? 'success' : 'warning'}
                  sx={{ fontSize: '0.7rem', height: '20px' }}
                />
                {message.processing_time && (
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    {message.processing_time.toFixed(2)}s
                  </Typography>
                )}
              </Box>
            )}
          </BubbleContent>

          {message.sources && message.sources.length > 0 && !isUser && (
            <Box sx={{ mt: 1 }}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  cursor: 'pointer',
                  opacity: 0.7,
                  '&:hover': { opacity: 1 }
                }}
                onClick={() => toggleSourceExpansion(message.id)}
              >
                <SourceIcon sx={{ fontSize: 16, mr: 0.5 }} />
                <Typography variant="caption">
                  {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                </Typography>
                {expandedSources[message.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </Box>
              
              <Collapse in={expandedSources[message.id]}>
                <Box sx={{ mt: 1 }}>
                  {message.sources.map((source, index) => (
                    <SourceCard key={index} variant="outlined">
                      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                        <Typography variant="caption" color="primary" fontWeight="bold">
                          {source.chapter_name}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 0.5 }}>
                          {source.content.length > 150 
                            ? source.content.substring(0, 150) + '...'
                            : source.content
                          }
                        </Typography>
                        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption" color="text.secondary">
                            {source.source_file}
                          </Typography>
                          <Chip
                            label={`Match: ${(1 / (1 + source.score) * 100).toFixed(0)}%`}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.6rem', height: '18px' }}
                          />
                        </Box>
                      </CardContent>
                    </SourceCard>
                  ))}
                </Box>
              </Collapse>
            </Box>
          )}
        </Box>
      </MessageBubble>
    );
  };

  if (!isOpen) {
    return (
      <Zoom in={!isOpen}>
        <FloatingChatButton onClick={openChat}>
          <ChatIcon />
        </FloatingChatButton>
      </Zoom>
    );
  }

  return (
    <ChatContainer>
      <ChatPaper>
        <ChatHeader>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BotIcon />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                AI Learning Assistant
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                Ask me about your course materials
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={closeChat} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </ChatHeader>

        <MessagesContainer>
          {messages.length === 0 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Start a conversation by asking me about your course materials!
            </Alert>
          )}
          
          {messages.map(renderMessage)}
          
          {isLoading && (
            <Box sx={{ width: '100%', mt: 1 }}>
              <LinearProgress />
              <Typography variant="caption" sx={{ mt: 1, opacity: 0.6 }}>
                AI is thinking...
              </Typography>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <Divider />
        
        <InputContainer>
          <TextField
            fullWidth
            placeholder="Ask me about your course..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            multiline
            maxRows={3}
            variant="outlined"
            size="small"
          />
          <IconButton
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            color="primary"
          >
            <SendIcon />
          </IconButton>
        </InputContainer>
      </ChatPaper>
    </ChatContainer>
  );
};

export default AIChatbot;
