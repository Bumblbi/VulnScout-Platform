import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import { Download, PictureAsPdf, Html } from '@mui/icons-material';
import { scanAPI } from '../../services/api';
import type { ScanTask } from '../../types';

const ReportGenerator: React.FC = () => {
  const [scanTasks, setScanTasks] = useState<ScanTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<string>('');
  const [reportFormat, setReportFormat] = useState<'pdf' | 'html'>('pdf');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadScanTasks();
  }, []);

  const loadScanTasks = async () => {
    try {
      setLoading(true);
      // Mock данные вместо API вызова
      const mockTasks: ScanTask[] = [
        {
          id: '1',
          target: 'example.com',
          mode: 'black',
          intensity: 'medium',
          status: 'completed',
          progress: 100,
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
        }
      ];
      setScanTasks(mockTasks);
    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка при загрузке задач сканирования' });
      console.error('Error loading scan tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    if (!selectedTask) {
      setMessage({ type: 'error', text: 'Выберите задачу сканирования' });
      return;
    }

    try {
      setGenerating(true);
      setMessage(null);

      // Временная заглушка для демонстрации
      setTimeout(() => {
        if (reportFormat === 'pdf') {
          // Создаем mock PDF
          const blob = new Blob(['Mock PDF report'], { type: 'application/pdf' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `vulnscan-report-${selectedTask}.pdf`;
          link.click();
          window.URL.revokeObjectURL(url);
        } else {
          // Для HTML
          const htmlContent = `
            <html>
              <head><title>VulnScan Report</title></head>
              <body>
                <h1>Report for scan ${selectedTask}</h1>
                <p>This is a mock HTML report</p>
              </body>
            </html>
          `;
          const blob = new Blob([htmlContent], { type: 'text/html' });
          const url = window.URL.createObjectURL(blob);
          window.open(url, '_blank');
        }

        setMessage({ type: 'success', text: 'Отчет успешно сгенерирован' });
        setGenerating(false);
      }, 2000);

    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка при генерации отчета' });
      console.error('Error generating report:', error);
      setGenerating(false);
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
      <Typography variant="h4" gutterBottom>
        Генератор отчетов
      </Typography>

      {/* ЗАМЕНА GRID НА BOX С CSS GRID */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' },
        gap: 3,
        mb: 3 
      }}>
        {/* Левая панель - настройки */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Настройки отчета
            </Typography>

            {message && (
              <Alert severity={message.type} sx={{ mb: 2 }}>
                {message.text}
              </Alert>
            )}

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Задача сканирования</InputLabel>
              <Select
                value={selectedTask}
                label="Задача сканирования"
                onChange={(e) => setSelectedTask(e.target.value)}
              >
                {scanTasks.map((task) => (
                  <MenuItem key={task.id} value={task.id}>
                    {task.target} - {new Date(task.createdAt).toLocaleDateString()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Формат отчета</InputLabel>
              <Select
                value={reportFormat}
                label="Формат отчета"
                onChange={(e) => setReportFormat(e.target.value as 'pdf' | 'html')}
              >
                <MenuItem value="pdf">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PictureAsPdf fontSize="small" />
                    PDF
                  </Box>
                </MenuItem>
                <MenuItem value="html">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Html fontSize="small" />
                    HTML
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              startIcon={generating ? <CircularProgress size={20} /> : <Download />}
              onClick={generateReport}
              disabled={!selectedTask || generating}
              fullWidth
              size="large"
            >
              {generating ? 'Генерация...' : 'Сгенерировать отчет'}
            </Button>
          </CardContent>
        </Card>

        {/* Правая панель - список задач */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Доступные задачи для отчетов
            </Typography>
            
            {loading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : scanTasks.length === 0 ? (
              <Alert severity="info">Нет завершенных задач сканирования</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Цель</TableCell>
                      <TableCell>Дата создания</TableCell>
                      <TableCell>Режим</TableCell>
                      <TableCell>Статус</TableCell>
                      <TableCell>Прогресс</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {scanTasks.map((task) => (
                      <TableRow 
                        key={task.id}
                        selected={selectedTask === task.id}
                        onClick={() => setSelectedTask(task.id)}
                        sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
                      >
                        <TableCell>{task.target}</TableCell>
                        <TableCell>
                          {new Date(task.createdAt).toLocaleDateString()}
                        </TableCell>
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
                              <CircularProgress 
                                variant="determinate" 
                                value={task.progress} 
                                size={24}
                                color={
                                  task.status === 'error' ? 'error' :
                                  task.status === 'completed' ? 'success' : 'primary'
                                }
                              />
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              {`${Math.round(task.progress)}%`}
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Информация о содержании отчета */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Содержание отчета
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Отчет будет содержать:
          </Typography>
          <ul>
            <li><Typography variant="body2">Общую информацию о сканировании</Typography></li>
            <li><Typography variant="body2">Список обнаруженных хостов и портов</Typography></li>
            <li><Typography variant="body2">Детальную информацию об уязвимостях с уровнями опасности</Typography></li>
            <li><Typography variant="body2">Рекомендации по устранению уязвимостей</Typography></li>
            <li><Typography variant="body2">Доказательства и скриншоты (если доступны)</Typography></li>
            <li><Typography variant="body2">Статистику и сводные данные</Typography></li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ReportGenerator;