import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
} from '@mui/material';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const severityColors = {
  critical: '#ff1744',
  high: '#ff9100',
  medium: '#ffeb3b',
  low: '#4caf50',
};

const Dashboard: React.FC = () => {
  // Mock данные для демонстрации
  const scanStats = {
    total: 150,
    completed: 120,
    running: 5,
    failed: 25,
  };

  const vulnerabilityStats = [
    { name: 'Critical', value: 12, color: severityColors.critical },
    { name: 'High', value: 34, color: severityColors.high },
    { name: 'Medium', value: 67, color: severityColors.medium },
    { name: 'Low', value: 89, color: severityColors.low },
  ];

  const recentScans = [
    { date: '2024-01-01', scans: 4 },
    { date: '2024-01-02', scans: 7 },
    { date: '2024-01-03', scans: 5 },
    { date: '2024-01-04', scans: 8 },
    { date: '2024-01-05', scans: 6 },
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Статистика сканирований */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
        gap: 3, 
        mb: 4 
      }}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Всего сканирований
            </Typography>
            <Typography variant="h4" component="div">
              {scanStats.total}
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Завершено
            </Typography>
            <Typography variant="h4" component="div" color="success.main">
              {scanStats.completed}
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              В работе
            </Typography>
            <Typography variant="h4" component="div" color="warning.main">
              {scanStats.running}
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Ошибки
            </Typography>
            <Typography variant="h4" component="div" color="error.main">
              {scanStats.failed}
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Графики */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 3 
      }}>
        {/* График уязвимостей - ИСПРАВЛЕННЫЙ */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Распределение уязвимостей
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={vulnerabilityStats}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {vulnerabilityStats.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name) => [`${value} уязвимостей`, name]}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Paper>

        {/* График сканирований */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Активность сканирований
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={recentScans}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="scans" 
                stroke="#8884d8" 
                activeDot={{ r: 8 }} 
                name="Количество сканирований"
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard;