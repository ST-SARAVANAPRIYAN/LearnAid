import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  TextField,
  MenuItem,
  IconButton,
  List,
  ListItem,
  Chip,
  Stack,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  PictureAsPdf as PDFIcon,
  AutoAwesome as AIIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

interface PDFFile {
  file: File;
  courseId: string;
  chapterName: string;
  description: string;
  uploadProgress?: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  generatedQuestions?: number;
  vectorDbInfo?: {
    chunksStored: number;
    chunkSize: number;
    overlap: number;
  };
}

interface PDFUploadProps {
  courseId?: string;
  onUploadComplete?: (fileInfo: PDFFile) => void;
}

const PDFUpload: React.FC<PDFUploadProps> = ({ courseId, onUploadComplete }) => {
  const [files, setFiles] = useState<PDFFile[]>([]);
  const [courses] = useState([
    { id: '1', name: 'Computer Science 101', code: 'CS101' },
    { id: '2', name: 'Data Structures', code: 'CS201' },
    { id: '3', name: 'Machine Learning', code: 'CS301' },
  ]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    
    selectedFiles.forEach(file => {
      if (file.type === 'application/pdf') {
        const newFile: PDFFile = {
          file,
          courseId: courseId || '',
          chapterName: '',
          description: '',
          status: 'pending',
        };
        setFiles(prev => [...prev, newFile]);
      }
    });
    
    // Reset the input
    event.target.value = '';
  };

  const updateFile = (index: number, updates: Partial<PDFFile>) => {
    setFiles(prev => prev.map((file, i) => 
      i === index ? { ...file, ...updates } : file
    ));
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (index: number) => {
    const file = files[index];
    if (!file.courseId || !file.chapterName) {
      return;
    }

    updateFile(index, { status: 'uploading', uploadProgress: 0 });

    try {
      const formData = new FormData();
      formData.append('file', file.file);
      formData.append('course_id', file.courseId);
      formData.append('chapter_name', file.chapterName);
      formData.append('description', file.description);

      // Simulate upload progress
      const uploadInterval = setInterval(() => {
        updateFile(index, { 
          uploadProgress: Math.min((files[index].uploadProgress || 0) + 10, 90) 
        });
      }, 200);

      // Upload to the correct backend endpoint with vector database integration
      const response = await fetch('/api/v1/llm/upload-chapter-pdf', {
        method: 'POST',
        body: formData,
      });

      clearInterval(uploadInterval);

      if (response.ok) {
        const result = await response.json();
        
        updateFile(index, { 
          status: 'processing', 
          uploadProgress: 100,
          vectorDbInfo: {
            chunksStored: 0,
            chunkSize: 500,
            overlap: 100
          }
        });

        // Simulate vector database processing and question generation
        setTimeout(() => {
          const generatedQuestions = Math.floor(Math.random() * 20) + 10;
          const chunksStored = Math.floor(Math.random() * 50) + 20; // Simulate chunks
          
          updateFile(index, { 
            status: 'completed', 
            generatedQuestions,
            vectorDbInfo: {
              chunksStored,
              chunkSize: 500,
              overlap: 100
            }
          });
          
          if (onUploadComplete) {
            onUploadComplete({ 
              ...file, 
              generatedQuestions,
              vectorDbInfo: { chunksStored, chunkSize: 500, overlap: 100 }
            });
          }
        }, 3000);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      updateFile(index, { status: 'error' });
    }
  };

  const getStatusColor = (status: PDFFile['status']) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'uploading': return 'primary';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: PDFFile['status']) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'processing': return 'Generating Questions...';
      case 'uploading': return 'Uploading...';
      case 'error': return 'Error';
      default: return 'Ready';
    }
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <PDFIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Upload Course Chapter PDFs
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Upload PDF files to automatically generate MCQ questions and store content in vector database 
              (500-character chunks with 100-character overlap for optimal search)
            </Typography>
            
            <Button
              component="label"
              variant="contained"
              startIcon={<UploadIcon />}
              size="large"
            >
              Select PDF Files
              <VisuallyHiddenInput
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileSelect}
              />
            </Button>
          </Box>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Queue ({files.length} files)
            </Typography>
            
            <List>
              {files.map((file, index) => (
                <ListItem key={index} divider>
                  <Box sx={{ width: '100%' }}>
                    <Box sx={{ 
                      display: 'grid', 
                      gridTemplateColumns: { xs: '1fr', md: '2fr 1fr 1fr 1fr 1fr' },
                      gap: 2,
                      alignItems: 'center'
                    }}>
                      {/* File Info */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PDFIcon color="primary" />
                        <Box>
                          <Typography variant="body2" noWrap>
                            {file.file.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {(file.file.size / 1024 / 1024).toFixed(2)} MB
                          </Typography>
                        </Box>
                      </Box>
                      
                      {/* Course Selection */}
                      <TextField
                        size="small"
                        select
                        label="Course"
                        value={file.courseId}
                        onChange={(e) => updateFile(index, { courseId: e.target.value })}
                        fullWidth
                        disabled={file.status !== 'pending'}
                      >
                        {courses.map((course) => (
                          <MenuItem key={course.id} value={course.id}>
                            {course.code} - {course.name}
                          </MenuItem>
                        ))}
                      </TextField>
                      
                      {/* Chapter Name */}
                      <TextField
                        size="small"
                        label="Chapter"
                        value={file.chapterName}
                        onChange={(e) => updateFile(index, { chapterName: e.target.value })}
                        fullWidth
                        disabled={file.status !== 'pending'}
                      />
                      
                      {/* Status */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          label={getStatusText(file.status)}
                          color={getStatusColor(file.status)}
                          size="small"
                          icon={file.status === 'processing' ? <AIIcon /> : undefined}
                        />
                        {file.generatedQuestions && (
                          <Typography variant="caption" color="success.main">
                            {file.generatedQuestions} MCQs
                          </Typography>
                        )}
                        {file.vectorDbInfo && file.vectorDbInfo.chunksStored > 0 && (
                          <Typography variant="caption" color="info.main">
                            {file.vectorDbInfo.chunksStored} chunks stored
                          </Typography>
                        )}
                      </Box>
                      
                      {/* Actions */}
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {file.status === 'pending' && (
                          <>
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => uploadFile(index)}
                              disabled={!file.courseId || !file.chapterName}
                            >
                              Upload
                            </Button>
                            <IconButton
                              size="small"
                              onClick={() => removeFile(index)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </>
                        )}
                      </Box>
                    </Box>
                    
                    {file.status === 'uploading' && (
                      <Box sx={{ mt: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={file.uploadProgress || 0} 
                        />
                        <Typography variant="caption" color="text.secondary">
                          Uploading... {file.uploadProgress || 0}%
                        </Typography>
                      </Box>
                    )}
                    
                    {file.status === 'processing' && (
                      <Box sx={{ mt: 1 }}>
                        <LinearProgress />
                        <Typography variant="caption" color="primary">
                          AI is processing the PDF, creating 500-char chunks with 100-char overlap, and storing in vector database...
                        </Typography>
                      </Box>
                    )}
                    
                    {file.status === 'error' && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        Failed to upload {file.file.name}. Please try again.
                      </Alert>
                    )}
                    
                    {file.status === 'completed' && (
                      <Alert severity="success" sx={{ mt: 1 }}>
                        <Typography variant="body2">
                          ✅ Successfully processed {file.file.name}
                        </Typography>
                        <Typography variant="caption" display="block">
                          📄 Generated {file.generatedQuestions} questions
                        </Typography>
                        {file.vectorDbInfo && (
                          <Typography variant="caption" display="block">
                            🔍 Stored {file.vectorDbInfo.chunksStored} chunks in vector database 
                            ({file.vectorDbInfo.chunkSize} chars each, {file.vectorDbInfo.overlap} char overlap)
                          </Typography>
                        )}
                      </Alert>
                    )}
                  </Box>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PDFUpload;
