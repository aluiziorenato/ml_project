import axios from 'axios';

export const fetchDashboardMetrics = async () => {
  // Exemplo: ajuste a URL conforme seu backend
  const response = await axios.get('/api/dashboard/metrics');
  return response.data;
};

export const fetchDashboardTableData = async (filters = {}) => {
  // Exemplo: ajuste a URL e params conforme seu backend
  const response = await axios.get('/api/dashboard/table', { params: filters });
  return response.data;
};
