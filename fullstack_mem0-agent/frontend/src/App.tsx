import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, Container, TextField, Button, Typography, CssBaseline, 
  AppBar, Toolbar, IconButton, Drawer, List, ListItem, ListItemText,
  Divider, CircularProgress, Dialog, DialogTitle, DialogContent,
  DialogContentText, DialogActions, Alert, ThemeProvider, createTheme
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DeleteIcon from '@mui/icons-material/Delete';
import LogoutIcon from '@mui/icons-material/Logout';
import SendIcon from '@mui/icons-material/Send';
import { v4 as uuidv4 } from 'uuid';

import { getCurrentUser, signOut, AuthUser } from './services/auth';
import { sendMessage, ChatMessage } from './services/api';
import ChatMessageComponent from './components/ChatMessage';
import LoginForm from './components/LoginForm';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#9c27b0',
    },
  },
});

const App: React.FC = () => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Check authentication status on load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        
        if (currentUser && !sessionId) {
          setSessionId(uuidv4());
        }
      } catch (err) {
        console.error('Auth check failed', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleLogin = async () => {
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    setSessionId(uuidv4());
  };

  const handleLogout = async () => {
    try {
      await signOut();
      setUser(null);
      setMessages([]);
      setSessionId('');
    } catch (err) {
      console.error('Logout failed', err);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !user) return;
    
    setIsSending(true);
    setError(null);
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: input
    };
    
    setMessages([...messages, userMessage]);
    setInput('');
    
    try {
      const response = await sendMessage({
        message: input.trim(),
        user_id: user.id,
        session_id: sessionId
      });
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (err: any) {
      setError('Failed to get response. Please try again.');
      console.error('Send message failed', err);
    } finally {
      setIsSending(false);
    }
  };

  const handleClearMemories = async () => {
    // Implement clear memories functionality
    setShowClearConfirm(false);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {!user ? (
        <LoginForm onLoginSuccess={handleLogin} />
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          <AppBar position="static">
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                🧠 Mem0 Chat
              </Typography>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {user.email}
              </Typography>
              <IconButton color="inherit" onClick={handleLogout}>
                <LogoutIcon />
              </IconButton>
            </Toolbar>
          </AppBar>
          
          <Drawer
            anchor="left"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
          >
            <Box
              sx={{ width: 250 }}
              role="presentation"
            >
              <List>
                <ListItem>
                  <Typography variant="h6">Mem0 Chat</Typography>
                </ListItem>
                <Divider />
                <ListItem 
                  button 
                  onClick={() => setShowClearConfirm(true)}
                  sx={{ color: 'error.main' }}
                >
                  <DeleteIcon sx={{ mr: 1 }} />
                  <ListItemText primary="Clear Memories" />
                </ListItem>
              </List>
            </Box>
          </Drawer>
          
          <Container 
            sx={{ 
              flexGrow: 1, 
              display: 'flex', 
              flexDirection: 'column',
              p: 2,
              overflow: 'hidden'
            }}
          >
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
            )}
            
            <Box 
              sx={{ 
                flexGrow: 1, 
                overflowY: 'auto',
                mb: 2,
                p: 1
              }}
            >
              {messages.map((message, index) => (
                <ChatMessageComponent key={index} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </Box>
            
            <Box 
              component="form" 
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              sx={{ 
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              <TextField
                fullWidth
                variant="outlined"
                label="Type your message"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isSending}
              />
              <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                onClick={handleSendMessage}
                disabled={!input.trim() || isSending}
              >
                {isSending ? <CircularProgress size={24} /> : 'Send'}
              </Button>
            </Box>
          </Container>
          
          <Dialog
            open={showClearConfirm}
            onClose={() => setShowClearConfirm(false)}
          >
            <DialogTitle>Clear All Memories?</DialogTitle>
            <DialogContent>
              <DialogContentText>
                This will permanently delete all of your memories from the AI.
                This action cannot be undone.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowClearConfirm(false)}>Cancel</Button>
              <Button onClick={handleClearMemories} color="error">
                Clear All Memories
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      )}
    </ThemeProvider>
  );
};

export default App; 