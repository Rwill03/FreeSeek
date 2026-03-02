import { useState, useEffect } from 'react';
import apiClient from '../api';

/**
 * Custom hook for managing job data, stats, and scheduler status
 */
export const useJobData = () => {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState(null);
  const [scanCheckInterval, setScanCheckInterval] = useState(null);

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
      
      // If scanning is in progress, set up frequent polling
      if (statusData.scanning) {
        if (scanCheckInterval) clearInterval(scanCheckInterval);
        const interval = setInterval(async () => {
          try {
            const [newStatsData, newJobsData, newStatusData] = await Promise.all([
              apiClient.getStats(),
              apiClient.getJobs(),
              apiClient.getSchedulerStatus(),
            ]);
            setStats(newStatsData);
            setJobs(newJobsData);
            setSchedulerStatus(newStatusData);
            
            // Clear interval when scanning is done
            if (!newStatusData.scanning) {
              clearInterval(interval);
              setScanCheckInterval(null);
            }
          } catch (err) {
            console.error('Error updating data during scan:', err);
          }
        }, 2000); // Poll every 2 seconds during scan
        setScanCheckInterval(interval);
      } else if (scanCheckInterval) {
        // Clear interval if scanning stopped
        clearInterval(scanCheckInterval);
        setScanCheckInterval(null);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Refresh data every 30 seconds (normal polling)
    const interval = setInterval(fetchData, 30000);
    
    return () => {
      clearInterval(interval);
      if (scanCheckInterval) clearInterval(scanCheckInterval);
    };
  }, [scanCheckInterval]);

  const handleRunScan = async () => {
    try {
      await apiClient.runScan();
      // Give the backend a moment to set the scanning flag
      await new Promise(resolve => setTimeout(resolve, 500));
      // Fetch the latest status (which should now show scanning: true)
      const statusData = await apiClient.getSchedulerStatus();
      setSchedulerStatus(statusData);
    } catch (err) {
      alert('Failed to start scan: ' + err.message);
    }
  };

  const handleGetLogs = async () => {
    try {
      setLogs({ logs: 'Loading logs...' });
      const logsData = await apiClient.getLogs();
      setLogs(logsData);
    } catch (err) {
      setLogs({ logs: 'Failed to fetch logs. Please try again.' });
      alert('Failed to fetch logs: ' + err.message);
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

  const handleMarkJobApplied = async (jobId) => {
    try {
      const result = await apiClient.markJobApplied(jobId);
      alert('Job marked as applied!');
      fetchData(); // Refresh data
      return result;
    } catch (err) {
      alert('Failed to mark job as applied: ' + err.message);
      return null;
    }
  };

  const clearLogs = () => setLogs(null);

  return {
    stats,
    jobs,
    schedulerStatus,
    loading,
    error,
    logs,
    handleRunScan,
    handleGetLogs,
    handleToggleAutoApply,
    handleGenerateProposal,
    handleMarkJobApplied,
    fetchData,
    clearLogs,
  };
};
