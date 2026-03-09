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
  MenuItem,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { ArrowBack as BackIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import Editor from '@monaco-editor/react';
import { taskService } from '../services/apiService';

const TASK_TYPES = [
  { value: 'python_script', label: 'Python Script' },
  { value: 'api_call', label: 'API Call' },
  { value: 'shell_command', label: 'Shell Command' },
  { value: 'file_operation', label: 'File Operation' },
];

function TaskCreate() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [taskType, setTaskType] = useState('python_script');
  const [scriptContent, setScriptContent] = useState('# Write your Python script here\n\n# Use the "parameters" variable to access passed parameters\n# Set "result" variable to return a value\n\nresult = {"status": "success"}');
  const [schedule, setSchedule] = useState('');
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const taskData = {
        name,
        description,
        task_type: taskType,
        script_content: scriptContent,
        parameters: {},
        schedule: schedule || null,
        enabled,
        timeout: 3600,
      };

      await taskService.createTask(taskData);
      enqueueSnackbar('Task created successfully', { variant: 'success' });
      navigate('/tasks');
    } catch (error) {
      enqueueSnackbar(error.response?.data?.detail || 'Failed to create task', {
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => navigate('/tasks')}>
            <BackIcon />
          </IconButton>
          <Typography variant="h6">Create New Task</Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              required
              label="Task Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
            />

            <TextField
              fullWidth
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              margin="normal"
              multiline
              rows={2}
            />

            <TextField
              fullWidth
              required
              select
              label="Task Type"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              margin="normal"
            >
              {TASK_TYPES.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <Box sx={{ mt: 2, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Script Content
              </Typography>
              <Paper sx={{ border: '1px solid #ddd' }}>
                <Editor
                  height="300px"
                  defaultLanguage="python"
                  value={scriptContent}
                  onChange={(value) => setScriptContent(value || '')}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                  }}
                />
              </Paper>
            </Box>

            <TextField
              fullWidth
              label="Schedule (Cron Expression)"
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              margin="normal"
              placeholder="0 9 * * * (Optional)"
              helperText="Leave empty for manual execution only"
            />

            <FormControlLabel
              control={<Switch checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />}
              label="Enabled"
            />

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                fullWidth
              >
                {loading ? 'Creating...' : 'Create Task'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/tasks')}
                fullWidth
              >
                Cancel
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default TaskCreate;
