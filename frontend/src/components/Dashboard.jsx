import { useMemo, useState } from 'react';
import apiClient from '../api';
import Header from './Header';
import StatsSection from './StatsSection';
import OperationsSection from './OperationsSection';
import JobsTable from './JobsTable';
import ProposalModal from './ProposalModal';
import LogsModal from './LogsModal';

const Dashboard = ({
  stats,
  jobs,
  schedulerStatus,
  logs,
  onRunScan,
  onToggleAutoApply,
  onGenerateProposal,
  onMarkJobApplied,
  onRefresh,
  onGetLogs,
  onClearLogs,
}) => {
  const [proposal, setProposal] = useState(null);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [showLogsModal, setShowLogsModal] = useState(false);

  const handleViewProposal = async (jobId) => {
    try {
      const proposalData = await apiClient.getProposal(jobId);
      setProposal(proposalData);
      setShowProposalModal(true);
    } catch (err) {
      alert('No proposal found for this job');
    }
  };

  const handleGetLogs = () => {
    onGetLogs();
    setShowLogsModal(true);
  };

  const statusCounts = useMemo(() => {
    return jobs.reduce((acc, job) => {
      const key = job.status || 'unknown';
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
  }, [jobs]);

  return (
    <div className="bg-background">
      <Header
        schedulerStatus={schedulerStatus}
        onRunScan={onRunScan}
        onRefresh={onRefresh}
        onGetLogs={handleGetLogs}
      />

      <main className="container-wide pb-16">
        <StatsSection stats={stats} />

        <OperationsSection
          schedulerStatus={schedulerStatus}
          statusCounts={statusCounts}
          onToggleAutoApply={onToggleAutoApply}
        />

        <JobsTable
          jobs={jobs}
          onGenerateProposal={onGenerateProposal}
          onMarkJobApplied={onMarkJobApplied}
          onViewProposal={handleViewProposal}
        />
      </main>

      {showProposalModal && proposal && (
        <ProposalModal
          proposal={proposal}
          onClose={() => setShowProposalModal(false)}
        />
      )}

      {showLogsModal && (
        <LogsModal
          logs={logs}
          onClose={() => setShowLogsModal(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
