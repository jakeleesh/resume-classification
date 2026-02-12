import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Container,
  Alert,
  LinearProgress,
  Grid,
  Divider
} from '@mui/material';
import './App.css';

// API base URL - change this if your backend runs on different host/port
const API_BASE_URL = 'http://localhost:8000';

function App() {
  // State management
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  };



  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Validation
    if (!selectedFile) {
      setError('Please select a resume PDF file');
      return;
    }

    setIsLoading(true);
    setError('');
    setPrediction(null);

    try {
      // Create form data to send file
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Call the API
      const response = await axios.post(
        `${API_BASE_URL}/api/predict`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setPrediction(response.data);
    } catch (err) {
      console.error('Error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to analyze resume. Make sure the backend is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPrediction(null);
    setError('');
    // Reset file input
    document.getElementById('fileInput').value = '';
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom>
          AI Resume Screening System
        </Typography>
        <Typography variant="subtitle1">
          Upload resume PDF
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1" gutterBottom>
                Upload Resume (PDF)
              </Typography>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                disabled={isLoading}
              >
                Choose File
                <input
                  id="fileInput"
                  type="file"
                  accept=".pdf"
                  hidden
                  onChange={handleFileChange}
                  disabled={isLoading}
                />
              </Button>
              {selectedFile && (
                <Alert severity="success" sx={{ mt: 1 }}>
                  Selected: {selectedFile.name}
                </Alert>
              )}
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={isLoading || !selectedFile}
              >
                {isLoading ? 'Analyzing...' : 'Analyze Resume'}
              </Button>
              <Button
                type="button"
                variant="outlined"
                fullWidth
                onClick={handleReset}
                disabled={isLoading}
              >
                Reset
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

      {prediction && (
        <Box>
          <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
            Analysis Results
          </Typography>

          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Candidate Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Name</Typography>
                  <Typography variant="body1">{prediction.candidate_name}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Email</Typography>
                  <Typography variant="body1">{prediction.email}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Phone</Typography>
                  <Typography variant="body1">{prediction.phone}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Experience</Typography>
                  <Typography variant="body1">{prediction.experience_years} years</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Education</Typography>
                  <Typography variant="body1">{prediction.education}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Skills</Typography>
                  <Typography variant="body1">{prediction.skills}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Card sx={{ mb: 2, backgroundColor: prediction.is_suitable ? '#e8f5e9' : '#ffebee' }}>
            <CardContent>
              <Typography 
                variant="h5" 
                gutterBottom
                sx={{ 
                  color: prediction.is_suitable ? '#2e7d32' : '#c62828',
                  fontWeight: 'bold'
                }}
              >
                Result: {prediction.is_suitable ? 'Selected' : 'Rejected'} for {prediction.recommended_role}
              </Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                The candidate was evaluated specifically for the <strong>{prediction.recommended_role}</strong> position.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Decision Confidence: {prediction.suitability_confidence}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={prediction.suitability_confidence} 
                  sx={{ 
                    height: 10, 
                    borderRadius: 1,
                    backgroundColor: '#e0e0e0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: prediction.is_suitable ? '#4caf50' : '#f44336'
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Role Analysis
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary">Best-Fit Role</Typography>
                <Typography variant="h6" sx={{ color: '#1976d2' }}>{prediction.recommended_role}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Role Match Confidence: {prediction.role_confidence}%
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="body2" gutterBottom sx={{ fontWeight: 'bold' }}>
                Alternative Role Matches
              </Typography>
              {prediction.top_3_roles.map((role, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">
                      {index + 1}. {role.role}
                    </Typography>
                    <Typography variant="body2">
                      {(role.confidence * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={role.confidence * 100}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>

        </Box>
      )}

      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="body2" color="text.secondary">
        </Typography>
      </Box>
    </Container>
  );
}

export default App;
