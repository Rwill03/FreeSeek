import { useState, useEffect } from 'react';
import apiClient from './api';
import Dashboard from './components/Dashboard';

function App() {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsData, jobsData, statusData] = await Promise.all([
        apiClient.getStats(),
        apiClient.getJobs(),
        apiClient.getSchedulerStatus(),
      ]);
      
      setStats(statsData);
      setJobs(jobsData);
      setSchedulerStatus(statusData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRunScan = async () => {
    try {
      await apiClient.runScan();
      alert('Job scan started! Check back in a few minutes.');
      // Refresh data after a delay
      setTimeout(fetchData, 5000);
    } catch (err) {
      alert('Failed to start scan: ' + err.message);
    }
  };

  const handleToggleAutoApply = async (enabled) => {
    try {
      await apiClient.toggleAutoApply(enabled);
      setSchedulerStatus({ ...schedulerStatus, auto_apply_enabled: enabled });
      alert(`Auto-apply ${enabled ? 'enabled' : 'disabled'}`);
    } catch (err) {
      alert('Failed to toggle auto-apply: ' + err.message);
    }
  };

  const handleGenerateProposal = async (jobId) => {
    try {
      const result = await apiClient.generateProposal(jobId);
      alert('Proposal generated successfully!');
      fetchData(); // Refresh data
      return result;
    } catch (err) {
      alert('Failed to generate proposal: ' + err.message);
      return null;
    }
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Dashboard
        stats={stats}
        jobs={jobs}
        schedulerStatus={schedulerStatus}
        onRunScan={handleRunScan}
        onToggleAutoApply={handleToggleAutoApply}
        onGenerateProposal={handleGenerateProposal}
        onRefresh={fetchData}
      />
    </div>
  );
}

export default App;
