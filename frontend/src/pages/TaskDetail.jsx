import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Grid,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { ArrowBack as BackIcon, PlayArrow as PlayIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { taskService } from '../services/apiService';

function TaskDetail() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    loadTask();
    loadExecutions();
  }, [taskId]);

  const loadTask = async () => {
    try {
      const data = await taskService.getTask(taskId);
      setTask(data);
    } catch (error) {
      enqueueSnackbar('Failed to load task', { variant: 'error' });
    }
  };

  const loadExecutions = async () => {
    try {
      const data = await taskService.getTaskExecutions(taskId);
      setExecutions(data);
    } catch (error) {
      console.error('Failed to load executions:', error);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    try {
      await taskService.executeTask(taskId);
      enqueueSnackbar('Task execution started', { variant: 'success' });
      setTimeout(loadExecutions, 1000); // Reload after 1 second
    } catch (error) {
      enqueueSnackbar('Failed to execute task', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await taskService.deleteTask(taskId);
      enqueueSnackbar('Task deleted successfully', { variant: 'success' });
      navigate('/tasks');
    } catch (error) {
      enqueueSnackbar('Failed to delete task', { variant: 'error' });
    }
  };

  if (!task) return <div>Loading...</div>;

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => navigate('/tasks')}>
            <BackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {task.name}
          </Typography>
          <Button
            color="inherit"
            startIcon={<PlayIcon />}
            onClick={handleExecute}
            disabled={loading}
          >
            Execute
          </Button>
          <IconButton color="inherit" onClick={() => setDeleteDialogOpen(true)}>
            <DeleteIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          {/* Task Details */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Task Details
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Type
                </Typography>
                <Chip label={task.task_type} size="small" sx={{ mt: 0.5 }} />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body1">{task.description || 'No description'}</Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={task.enabled ? 'Enabled' : 'Disabled'}
                  color={task.enabled ? 'success' : 'default'}
                  size="small"
                  sx={{ mt: 0.5 }}
                />
              </Box>
              {task.schedule && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Schedule
                  </Typography>
                  <Typography variant="body1">{task.schedule}</Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Script Content */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Script Content
              </Typography>
              <Box
                component="pre"
                sx={{
                  bgcolor: '#f5f5f5',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 300,
                }}
              >
                <code>{task.script_content}</code>
              </Box>
            </Paper>
          </Grid>

          {/* Execution History */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Execution History
              </Typography>
              {executions.length === 0 ? (
                <Typography color="text.secondary">No executions yet</Typography>
              ) : (
                executions.map((execution) => (
                  <Card key={execution.id} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle2">
                          {new Date(execution.created_at).toLocaleString()}
                        </Typography>
                        <Chip
                          label={execution.status}
                          color={
                            execution.status === 'completed'
                              ? 'success'
                              : execution.status === 'failed'
                              ? 'error'
                              : execution.status === 'running'
                              ? 'primary'
                              : 'default'
                          }
                          size="small"
                        />
                      </Box>
                      {execution.error && (
                        <Typography variant="body2" color="error">
                          Error: {execution.error}
                        </Typography>
                      )}
                      {execution.logs && (
                        <Box
                          component="pre"
                          sx={{
                            bgcolor: '#f5f5f5',
                            p: 1,
                            borderRadius: 1,
                            fontSize: 12,
                            overflow: 'auto',
                            maxHeight: 100,
                          }}
                        >
                          {execution.logs}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Task</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this task?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default TaskDetail;
