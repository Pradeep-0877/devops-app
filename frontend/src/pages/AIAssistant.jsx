import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { ArrowBack as BackIcon, Send as SendIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { aiService, taskService } from '../services/apiService';

function AIAssistant() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [generatedTask, setGeneratedTask] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setResponse('');
    setGeneratedTask(null);

    try {
      // First, get AI response
      const aiResponse = await aiService.processPrompt(prompt);
      setResponse(aiResponse.response);

      // Try to generate a task definition
      try {
        const taskDef = await aiService.generateTask(prompt);
        setGeneratedTask(taskDef);
      } catch (error) {
        console.log('Could not generate task definition');
      }
    } catch (error) {
      enqueueSnackbar('Failed to process prompt', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (!generatedTask) return;

    try {
      const task = await taskService.createTask({
        ...generatedTask,
        parameters: generatedTask.parameters || {},
        timeout: 3600,
        enabled: true,
      });
      
      enqueueSnackbar('Task created successfully!', { variant: 'success' });
      navigate(`/tasks/${task.id}`);
    } catch (error) {
      enqueueSnackbar('Failed to create task', { variant: 'error' });
    }
  };

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => navigate('/dashboard')}>
            <BackIcon />
          </IconButton>
          <Typography variant="h6">AI Assistant</Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Describe what you want to automate
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Use natural language to describe your automation task. The AI will help you create it.
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Describe your automation task"
              placeholder="Example: Send me an email with server stats every morning at 9 AM"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={loading}
            />

            <Button
              type="submit"
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              disabled={loading || !prompt.trim()}
              sx={{ mt: 2 }}
              fullWidth
            >
              {loading ? 'Processing...' : 'Generate Task'}
            </Button>
          </Box>

          {/* AI Response */}
          {response && (
            <Paper sx={{ p: 3, mt: 3, bgcolor: '#f5f5f5' }}>
              <Typography variant="h6" gutterBottom>
                AI Response
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {response}
              </Typography>
            </Paper>
          )}

          {/* Generated Task */}
          {generatedTask && (
            <Paper sx={{ p: 3, mt: 3, border: '2px solid #1976d2' }}>
              <Typography variant="h6" gutterBottom>
                Generated Task
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Name
                </Typography>
                <Typography variant="body1">{generatedTask.name}</Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body1">{generatedTask.description}</Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Type
                </Typography>
                <Typography variant="body1">{generatedTask.task_type}</Typography>
              </Box>

              {generatedTask.schedule && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Schedule
                  </Typography>
                  <Typography variant="body1">{generatedTask.schedule}</Typography>
                </Box>
              )}

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Script Content
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    bgcolor: '#fff',
                    p: 2,
                    borderRadius: 1,
                    overflow: 'auto',
                    maxHeight: 200,
                  }}
                >
                  <code>{generatedTask.script_content}</code>
                </Box>
              </Box>

              <Button
                variant="contained"
                onClick={handleCreateTask}
                fullWidth
              >
                Create This Task
              </Button>
            </Paper>
          )}

          {/* Examples */}
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Example Prompts
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {[
                'Check server CPU usage and alert me if it exceeds 80%',
                'Backup my database every night at midnight',
                'Send a daily summary email at 9 AM with yesterday\'s analytics',
                'Monitor website uptime and notify me if it\'s down',
                'Clean up old log files older than 30 days every week',
              ].map((example, idx) => (
                <Paper
                  key={idx}
                  sx={{
                    p: 2,
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                  onClick={() => setPrompt(example)}
                >
                  <Typography variant="body2">{example}</Typography>
                </Paper>
              ))}
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default AIAssistant;
