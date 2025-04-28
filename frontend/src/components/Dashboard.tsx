import React from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper,
  Button,
  Avatar
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <Container maxWidth="sm">
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mt: 8,
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main', mb: 2 }}>
            <PersonIcon sx={{ fontSize: 40 }} />
          </Avatar>
          <Typography component="h1" variant="h4" sx={{ fontWeight: 600, mb: 2 }}>
            Welcome to Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            You have successfully logged in to your account.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleLogout}
            sx={{ 
              py: 1.5,
              px: 4,
              fontSize: '1rem',
            }}
          >
            Logout
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Dashboard; 