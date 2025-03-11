import React from 'react';
import { Paper, Typography, Box, Avatar } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: {
    role: 'user' | 'assistant';
    content: string;
  };
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        mb: 2,
        gap: 1,
      }}
    >
      <Avatar 
        sx={{ 
          bgcolor: isUser ? 'primary.main' : 'secondary.main',
          alignSelf: 'flex-start',
        }}
      >
        {isUser ? <PersonIcon /> : <SmartToyIcon />}
      </Avatar>
      
      <Paper 
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '70%',
          backgroundColor: isUser ? 'primary.light' : 'grey.100',
          borderRadius: 2,
          wordBreak: 'break-word',
        }}
      >
        {isUser ? (
          <Typography variant="body1">{message.content}</Typography>
        ) : (
          <Typography variant="body1" component="div">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ChatMessage; 