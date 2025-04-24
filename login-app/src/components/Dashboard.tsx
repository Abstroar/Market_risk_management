import React from 'react';
import { 
  Box, 
  Typography, 
  Card,
  CardContent
} from '@mui/material';

const Dashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Market Dashboard
      </Typography>
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 2 
      }}>
        {/* Stock Graph */}
        <Card sx={{ width: '48%', minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6">Stock Performance</Typography>
            <Box sx={{ 
              width: '100%', 
              height: '200px', 
              bgcolor: '#f5f5f5',
              mt: 2,
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-around'
            }}>
              {[30, 50, 70, 40, 60, 80].map((height, index) => (
                <Box
                  key={index}
                  sx={{
                    width: '30px',
                    height: `${height}%`,
                    bgcolor: '#1976d2'
                  }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>

        {/* Prediction */}
        <Card sx={{ width: '48%', minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6">Market Prediction</Typography>
            <Box sx={{ 
              height: '200px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              mt: 2
            }}>
              <Typography variant="h6" color="primary">
                Bullish Trend Expected
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* News */}
        <Card sx={{ width: '48%', minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6">Market News</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography>• Market shows positive growth</Typography>
              <Typography>• New regulations announced</Typography>
              <Typography>• Tech sector leads gains</Typography>
              <Typography>• Global markets stable</Typography>
            </Box>
          </CardContent>
        </Card>

        {/* China & India Markets */}
        <Card sx={{ width: '48%', minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6">China & India Markets</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography>China: +2.5%</Typography>
              <Typography>India: +1.8%</Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Shanghai Composite: 3,450.67</Typography>
                <Typography variant="subtitle2">Nifty 50: 18,234.50</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard; 