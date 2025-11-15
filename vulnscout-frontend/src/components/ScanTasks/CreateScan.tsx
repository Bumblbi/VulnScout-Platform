import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Typography,
  Alert,
} from '@mui/material';
import { scanAPI } from '../../services/api';

const CreateScan: React.FC = () => {
  const [formData, setFormData] = useState({
    target: '',
    mode: 'black' as 'black' | 'gray' | 'white',
    intensity: 'medium' as 'low' | 'medium' | 'high',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await scanAPI.createTask(formData);
      setMessage({ type: 'success', text: 'Сканирование успешно запущено' });
      setFormData({ target: '', mode: 'black', intensity: 'medium' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка при запуске сканирования' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string) => (event: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Создание задачи сканирования
        </Typography>

        {message && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {/* ЗАМЕНА GRID НА BOX С CSS GRID */}
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            gap: 3 
          }}>
            <TextField
              fullWidth
              label="Цель (IP/домен)"
              value={formData.target}
              onChange={handleChange('target')}
              required
              placeholder="example.com или 192.168.1.1"
            />

            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
              gap: 3 
            }}>
              <FormControl fullWidth>
                <InputLabel>Режим сканирования</InputLabel>
                <Select
                  value={formData.mode}
                  label="Режим сканирования"
                  onChange={handleChange('mode')}
                >
                  <MenuItem value="black">Черный ящик</MenuItem>
                  <MenuItem value="gray">Серый ящик</MenuItem>
                  <MenuItem value="white">Белый ящик</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Интенсивность</InputLabel>
                <Select
                  value={formData.intensity}
                  label="Интенсивность"
                  onChange={handleChange('intensity')}
                >
                  <MenuItem value="low">Низкая</MenuItem>
                  <MenuItem value="medium">Средняя</MenuItem>
                  <MenuItem value="high">Высокая</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              fullWidth
              size="large"
            >
              {loading ? 'Запуск...' : 'Запуск сканирования'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default CreateScan;