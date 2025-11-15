import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import { scanAPI } from '../../services/api';
import type { ScanResult, Vulnerability, Host, Port } from '../../types';
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scan-details-tabpanel-${index}`}
      aria-labelledby={`scan-details-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

interface ScanDetailsProps {
  scanId: string;
}

const ScanDetails: React.FC<ScanDetailsProps> = ({ scanId }) => {
  const [tabValue, setTabValue] = useState(0);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScanDetails();
  }, [scanId]);

  const loadScanDetails = async () => {
    try {
      setLoading(true);
      const response = await scanAPI.getResults(scanId);
      setScanResult(response.data);
    } catch (err) {
      setError('Ошибка при загрузке деталей сканирования');
      console.error('Error loading scan details:', err);
    } finally {
      setLoading(false);
    }
  };

 const handleTabChange = (event: React.SyntheticEvent | null, newValue: number) => {
    setTabValue(newValue);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'critical': return 'Критический';
      case 'high': return 'Высокий';
      case 'medium': return 'Средний';
      case 'low': return 'Низкий';
      default: return severity;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!scanResult) {
    return <Alert severity="warning">Данные сканирования не найдены</Alert>;
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        Детали сканирования
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        ID: {scanId}
      </Typography>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="scan details tabs">
          <Tab label="Найденные хосты" />
          <Tab label="Открытые порты" />
          <Tab label="Уязвимости" />
        </Tabs>

        {/* Вкладка хостов */}
        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>IP Адрес</TableCell>
                  <TableCell>Имя хоста</TableCell>
                  <TableCell>Операционная система</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scanResult.hosts.map((host: Host) => (
                  <TableRow key={host.ip}>
                    <TableCell>{host.ip}</TableCell>
                    <TableCell>{host.hostname || 'N/A'}</TableCell>
                    <TableCell>{host.os || 'Не определено'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Вкладка портов */}
        <TabPanel value={tabValue} index={1}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Порт</TableCell>
                  <TableCell>Протокол</TableCell>
                  <TableCell>Сервис</TableCell>
                  <TableCell>Статус</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scanResult.ports.map((port: Port) => (
                  <TableRow key={`${port.number}-${port.protocol}`}>
                    <TableCell>{port.number}</TableCell>
                    <TableCell>{port.protocol}</TableCell>
                    <TableCell>{port.service}</TableCell>
                    <TableCell>
                      <Chip 
                        label={port.state} 
                        color={port.state === 'open' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Вкладка уязвимостей */}
        <TabPanel value={tabValue} index={2}>
          {scanResult.vulnerabilities.length === 0 ? (
            <Alert severity="info">Уязвимости не обнаружены</Alert>
          ) : (
            scanResult.vulnerabilities.map((vuln: Vulnerability) => (
              <Card key={vuln.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {vuln.title}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip 
                        label={getSeverityText(vuln.severity)}
                        color={getSeverityColor(vuln.severity) as any}
                        size="small"
                      />
                      <Chip 
                        label={`CVSS: ${vuln.cvssScore}`}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {vuln.description}
                  </Typography>

                  {vuln.host && vuln.port && (
                    <Typography variant="body2" paragraph>
                      <strong>Расположение:</strong> {vuln.host}:{vuln.port}
                    </Typography>
                  )}

                  {vuln.proof && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Доказательство:
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50' }}>
                        <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                          {vuln.proof}
                        </Typography>
                      </Paper>
                    </Box>
                  )}

                  <Box>
                    <Typography variant="subtitle2" gutterBottom color="primary">
                      Рекомендации по устранению:
                    </Typography>
                    <Typography variant="body2">
                      {vuln.recommendation}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))
          )}
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default ScanDetails;