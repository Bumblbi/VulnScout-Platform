import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton,
  Chip,
  Typography,
  Button,
} from '@mui/material';
import { Stop, Refresh } from '@mui/icons-material';
import { scanAPI } from '../../services/api';
import type { ScanTask } from '../../types'; // Используем type-only import

const ScanList: React.FC = () => {
  const [tasks, setTasks] = useState<ScanTask[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTasks = async () => {
    try {
      // Mock данные вместо API вызова
      const mockTasks: ScanTask[] = [
        {
          id: '1',
          target: 'example.com',
          mode: 'black',
          intensity: 'medium',
          status: 'running',
          progress: 45,
          createdAt: '2024-01-15T10:00:00Z'
        },
        {
          id: '2',
          target: '192.168.1.1',
          mode: 'gray', 
          intensity: 'high',
          status: 'completed',
          progress: 100,
          createdAt: '2024-01-16T14:30:00Z'
        },
        {
          id: '3',
          target: 'test.org',
          mode: 'white',
          intensity: 'low',
          status: 'error',
          progress: 30,
          createdAt: '2024-01-17T09:15:00Z'
        }
      ];
      setTasks(mockTasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleStopTask = async (taskId: string) => {
    try {
      await scanAPI.stopTask(taskId);
      await loadTasks(); // Перезагружаем список
    } catch (error) {
      console.error('Error stopping task:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'В ожидании';
      case 'running': return 'В работе';
      case 'completed': return 'Завершено';
      case 'error': return 'Ошибка';
      default: return status;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Задачи сканирования</Typography>
        <Button
          startIcon={<Refresh />}
          onClick={loadTasks}
          variant="outlined"
        >
          Обновить
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Цель</TableCell>
              <TableCell>Режим</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Прогресс</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.map((task) => (
              <TableRow key={task.id}>
                <TableCell>{task.id.slice(0, 8)}...</TableCell>
                <TableCell>{task.target}</TableCell>
                <TableCell>
                  <Chip 
                    label={task.mode === 'black' ? 'Черный ящик' : 
                           task.mode === 'gray' ? 'Серый ящик' : 'Белый ящик'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusText(task.status)} 
                    color={getStatusColor(task.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={task.progress} 
                        color={
                          task.status === 'error' ? 'error' :
                          task.status === 'completed' ? 'success' : 'primary'
                        }
                      />
                    </Box>
                    <Box sx={{ minWidth: 35 }}>
                      <Typography variant="body2" color="text.secondary">
                        {`${Math.round(task.progress)}%`}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  {task.status === 'running' && (
                    <IconButton
                      color="error"
                      onClick={() => handleStopTask(task.id)}
                      title="Остановить сканирование"
                    >
                      <Stop />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ScanList;