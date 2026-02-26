import { useState } from 'react';
import apiClient from '../api';

const Dashboard = ({
  stats,
  jobs,
  schedulerStatus,
  onRunScan,
  onToggleAutoApply,
  onGenerateProposal,
  onRefresh,
}) => {
  const [selectedJob, setSelectedJob] = useState(null);
  const [proposal, setProposal] = useState(null);
  const [showProposalModal, setShowProposalModal] = useState(false);

  const handleViewProposal = async (jobId) => {
    try {
      const proposalData = await apiClient.getProposal(jobId);
      setProposal(proposalData);
      setShowProposalModal(true);
    } catch (err) {
      alert('No proposal found for this job');
    }
  };

  const handleViewJob = (job) => {
    setSelectedJob(job);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied':
        return 'bg-green-100 text-green-800';
      case 'proposal_generated':
        return 'bg-blue-100 text-blue-800';
      case 'new':
        return 'bg-yellow-100 text-yellow-800';
      case 'manual_review':
        return 'bg-orange-100 text-orange-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'filtered':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          Freelance Auto Hunter
        </h1>
        <p className="text-gray-600">
          Automated job hunting and application system
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <StatCard
          title="Jobs Found Today"
          value={stats?.jobs_found_today || 0}
          color="blue"
        />
        <StatCard
          title="Applications Sent"
          value={stats?.applications_sent_today || 0}
          color="green"
        />
        <StatCard
          title="Pending Manual"
          value={stats?.pending_manual || 0}
          color="orange"
        />
        <StatCard
          title="Failed Today"
          value={stats?.failed_today || 0}
          color="red"
        />
        <StatCard
          title="Success Rate"
          value={`${stats?.success_rate || 0}%`}
          color="purple"
        />
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">Control Panel</h2>
        
        <div className="flex flex-wrap gap-4 mb-4">
          <button
            onClick={onRunScan}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            🔍 Run Job Scan Now
          </button>
          
          <button
            onClick={onRefresh}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
          >
            🔄 Refresh Data
          </button>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={schedulerStatus?.auto_apply_enabled || false}
              onChange={(e) => onToggleAutoApply(e.target.checked)}
              className="w-5 h-5"
            />
            <span className="text-lg font-medium">
              Auto-Apply {schedulerStatus?.auto_apply_enabled ? '✅' : '❌'}
            </span>
          </label>
          
          <div className="text-sm text-gray-600">
            ({schedulerStatus?.applications_today || 0} / {schedulerStatus?.max_applications_per_day || 10} applications today)
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-500">
          Scheduler: {schedulerStatus?.running ? '🟢 Running' : '🔴 Stopped'} | 
          Runs every 3 hours (8am-6pm, weekdays only)
        </div>
      </div>

      {/* Jobs Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-2xl font-semibold">Jobs ({jobs.length})</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                    No jobs found. Click "Run Job Scan Now" to start.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {job.title}
                      </div>
                      <div className="text-sm text-gray-500">
                        {job.location}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {job.company}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 uppercase">
                      {job.platform}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-sm font-semibold text-gray-900">
                          {job.match_score}
                        </div>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${job.match_score}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                          job.status
                        )}`}
                      >
                        {job.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(job.created_at)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium space-x-2">
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Job
                      </a>
                      {job.status === 'proposal_generated' || job.status === 'applied' ? (
                        <button
                          onClick={() => handleViewProposal(job.id)}
                          className="text-green-600 hover:text-green-900"
                        >
                          View Proposal
                        </button>
                      ) : job.status === 'new' ? (
                        <button
                          onClick={() => onGenerateProposal(job.id)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          Generate
                        </button>
                      ) : null}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Proposal Modal */}
      {showProposalModal && proposal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-semibold">Generated Proposal</h3>
                <button
                  onClick={() => setShowProposalModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="mb-4 text-sm text-gray-500">
                Job ID: {proposal.job_id} | Generated: {formatDate(proposal.generated_at)}
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
                {proposal.content}
              </div>
              
              <div className="mt-4 flex justify-end gap-2">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(proposal.content);
                    alert('Proposal copied to clipboard!');
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Copy to Clipboard
                </button>
                <button
                  onClick={() => setShowProposalModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ title, value, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800">{value}</p>
        </div>
        <div className={`${colorClasses[color]} w-12 h-12 rounded-lg opacity-20`} />
      </div>
    </div>
  );
};

export default Dashboard;
