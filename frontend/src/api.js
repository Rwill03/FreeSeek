import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Get dashboard stats
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },

  // Get jobs list
  getJobs: async (status = null, limit = 100) => {
    const params = {};
    if (status) params.status = status;
    if (limit) params.limit = limit;
    const response = await api.get('/jobs', { params });
    return response.data;
  },

  // Get single job
  getJob: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  // Get proposal for job
  getProposal: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}/proposal`);
    return response.data;
  },

  // Run job scan
  runScan: async () => {
    const response = await api.post('/scan', { manual: true });
    return response.data;
  },

  // Generate proposal
  generateProposal: async (jobId) => {
    const response = await api.post('/generate-proposal', { job_id: jobId });
    return response.data;
  },

  // Toggle auto-apply
  toggleAutoApply: async (enabled) => {
    const response = await api.post('/toggle-auto-apply', { enabled });
    return response.data;
  },

  // Get scheduler status
  getSchedulerStatus: async () => {
    const response = await api.get('/scheduler/status');
    return response.data;
  },

  // Get LLM logs
  getLogs: async () => {
    const response = await api.get('/logs');
    return response.data;
  },

  // Mark job as applied
  markJobApplied: async (jobId) => {
    const response = await api.post('/jobs/mark-applied', { job_id: jobId });
    return response.data;
  },
};

export default apiClient;
