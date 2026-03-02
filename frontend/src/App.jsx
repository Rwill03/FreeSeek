import { useJobData } from './hooks/useJobData';
import Dashboard from './components/Dashboard';

function App() {
  const {
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
  } = useJobData();

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-lg text-muted-foreground">Loading dashboard...</div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-lg text-destructive">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Dashboard
        stats={stats}
        jobs={jobs}
        schedulerStatus={schedulerStatus}
        logs={logs}
        onRunScan={handleRunScan}
        onToggleAutoApply={handleToggleAutoApply}
        onGenerateProposal={handleGenerateProposal}
        onMarkJobApplied={handleMarkJobApplied}
        onRefresh={fetchData}
        onGetLogs={handleGetLogs}
        onClearLogs={clearLogs}
      />
    </div>
  );
}

export default App;
