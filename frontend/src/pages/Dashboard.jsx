import React, { useState, useEffect, useContext } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  SmartToy as AIIcon,
  ExitToApp as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { taskService } from '../services/apiService';

function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total: 0, running: 0, completed: 0 });
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await taskService.getTasks();
      setTasks(data);
      
      // Calculate stats
      setStats({
        total: data.length,
        running: data.filter(t => t.enabled).length,
        completed: data.length,
      });
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Automation Platform
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            {user?.username}
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography color="text.secondary" gutterBottom>
                Total Tasks
              </Typography>
              <Typography variant="h3">{stats.total}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography color="text.secondary" gutterBottom>
                Active Tasks
              </Typography>
              <Typography variant="h3">{stats.running}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography color="text.secondary" gutterBottom>
                Executions
              </Typography>
              <Typography variant="h3">{stats.completed}</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <AddIcon sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6">Create Task</Typography>
                <Typography variant="body2" color="text.secondary">
                  Create a new automation task
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => navigate('/tasks/create')}>
                  Create
                </Button>
              </CardActions>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <PlayIcon sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6">View Tasks</Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage and execute tasks
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => navigate('/tasks')}>
                  View All
                </Button>
              </CardActions>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <AIIcon sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6">AI Assistant</Typography>
                <Typography variant="body2" color="text.secondary">
                  Create tasks with AI help
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => navigate('/ai-assistant')}>
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Tasks */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Recent Tasks
        </Typography>
        <Paper sx={{ p: 2 }}>
          {tasks.length === 0 ? (
            <Typography color="text.secondary">No tasks yet. Create your first task!</Typography>
          ) : (
            tasks.slice(0, 5).map((task) => (
              <Box
                key={task.id}
                sx={{
                  p: 2,
                  mb: 1,
                  border: '1px solid #ddd',
                  borderRadius: 1,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
                onClick={() => navigate(`/tasks/${task.id}`)}
              >
                <Typography variant="h6">{task.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {task.description || 'No description'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Type: {task.task_type} | Status: {task.enabled ? 'Enabled' : 'Disabled'}
                </Typography>
              </Box>
            ))
          )}
        </Paper>
      </Container>
    </Box>
  );
}

export default Dashboard;
