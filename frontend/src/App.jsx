import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import TaskCreate from './pages/TaskCreate';
import TaskDetail from './pages/TaskDetail';
import AIAssistant from './pages/AIAssistant';
import { AuthContext } from './context/AuthContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored token
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
    }
    
    setLoading(false);
  }, []);

  const login = (userData, tokens) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <AuthContext.Provider value={{ user, login, logout }}>
          <Router>
            <Routes>
              <Route 
                path="/login" 
                element={!user ? <Login /> : <Navigate to="/dashboard" />} 
              />
              <Route
                path="/dashboard"
                element={user ? <Dashboard /> : <Navigate to="/login" />}
              />
              <Route
                path="/tasks"
                element={user ? <Tasks /> : <Navigate to="/login" />}
              />
              <Route
                path="/tasks/create"
                element={user ? <TaskCreate /> : <Navigate to="/login" />}
              />
              <Route
                path="/tasks/:taskId"
                element={user ? <TaskDetail /> : <Navigate to="/login" />}
              />
              <Route
                path="/ai-assistant"
                element={user ? <AIAssistant /> : <Navigate to="/login" />}
              />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
          </Router>
        </AuthContext.Provider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
