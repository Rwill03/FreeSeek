import { useState } from 'react';
import apiClient from '../api';

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

  const getStatusStyles = (status) => {
    switch (status) {
      case 'applied':
        return 'bg-accent-2 text-accent-2-vivid';
      case 'proposal_generated':
        return 'bg-accent-1 text-accent-1-vivid';
      case 'new':
        return 'bg-secondary text-foreground';
      case 'manual_review':
        return 'bg-accent-3 text-accent-3-vivid';
      case 'failed':
        return 'bg-destructive/10 text-destructive';
      case 'filtered':
        return 'bg-secondary text-muted-foreground';
      default:
        return 'bg-secondary text-muted-foreground';
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
    <div className="bg-background">
      <header className="section-padding pb-12">
        <div className="container-wide">
          <div className="relative overflow-hidden rounded-2xl border border-border/50 bg-card shadow-sm">
            <div className="absolute inset-0 bg-gradient-hero opacity-80" aria-hidden="true" />
            <div className="relative p-6 md:p-10 lg:p-12">
              <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
                <div className="max-w-2xl">
                  <p className="text-xs font-medium uppercase tracking-tight text-muted-foreground">
                    Freelance Operations
                  </p>
                  <h1 className="mt-3 text-4xl font-semibold tracking-tight text-foreground md:text-5xl lg:text-6xl">
                    Freelance Auto Hunter
                  </h1>
                  <p className="mt-4 text-lg text-muted-foreground md:text-xl">
                    Automated job discovery and proposal management with a calm, engineering-first workflow.
                  </p>
                </div>
                <div className="flex flex-col gap-3 sm:flex-row items-stretch">
                  <button
                    onClick={onRunScan}
                    disabled={schedulerStatus?.scanning}
                    className={`rounded-lg px-6 py-3 text-sm font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
                      schedulerStatus?.scanning
                        ? 'bg-primary/80 text-primary-foreground cursor-not-allowed'
                        : 'bg-primary text-primary-foreground shadow-sm hover:shadow-lg'
                    }`}
                  >
                    {schedulerStatus?.scanning ? (
                      <>
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent"></div>
                        Scanning...
                      </>
                    ) : (
                      'Run Job Scan'
                    )}
                  </button>
                  <button
                    onClick={onRefresh}
                    className="rounded-lg border-2 border-primary px-6 py-3 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
                  >
                    Refresh Data
                  </button>
                  <button
                    onClick={() => {
                      onGetLogs();
                      setShowLogsModal(true);
                    }}
                    className="rounded-lg border-2 border-muted-foreground px-6 py-3 text-sm font-medium text-muted-foreground transition-colors duration-300 hover:border-foreground hover:text-foreground"
                  >
                    View Logs
                  </button>
                </div>
              </div>
              <div className="mt-8 flex flex-wrap items-center gap-3 text-xs font-medium text-muted-foreground">
                <span className="rounded-full bg-secondary px-3 py-1">
                  Scheduler: {schedulerStatus?.running ? 'Running' : 'Stopped'}
                </span>
                <span className="rounded-full bg-secondary px-3 py-1">
                  Auto-apply {schedulerStatus?.auto_apply_enabled ? 'enabled' : 'disabled'}
                </span>
                <span>
                  Runs every 3 hours (24/7, no time limits)
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container-wide pb-16">
        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
          <StatCard
            title="Jobs Found Today"
            value={stats?.jobs_found_today || 0}
            accent="bg-accent-1"
          />
          <StatCard
            title="Applications Sent"
            value={stats?.applications_sent_today || 0}
            accent="bg-accent-2"
          />
          <StatCard
            title="Pending Manual"
            value={stats?.pending_manual || 0}
            accent="bg-accent-3"
          />
          <StatCard
            title="Failed Today"
            value={stats?.failed_today || 0}
            accent="bg-destructive/10"
          />
          <StatCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            accent="bg-secondary"
          />
        </section>

        <section className="mt-8 rounded-2xl border border-border/50 bg-card p-6 shadow-sm transition-all duration-300 hover:border-border hover:shadow-lg md:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-foreground">Control Panel</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Manage scanning, refresh cadence, and auto-apply limits.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                onClick={onRunScan}
                className="rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-all duration-300 hover:shadow-lg"
              >
                Run Job Scan
              </button>
              <button
                onClick={onRefresh}
                className="rounded-lg border-2 border-primary px-6 py-3 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
              >
                Refresh Data
              </button>
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <label className="flex items-center justify-between rounded-lg border border-border/60 bg-background-subtle p-4 text-sm text-foreground">
              <span className="font-medium">Auto-apply</span>
              <input
                type="checkbox"
                checked={schedulerStatus?.auto_apply_enabled || false}
                onChange={(e) => onToggleAutoApply(e.target.checked)}
                className="h-5 w-5 accent-primary"
              />
            </label>
            <div className="rounded-lg border border-border/60 bg-background-subtle p-4 text-sm text-muted-foreground">
              {schedulerStatus?.applications_today || 0} / {schedulerStatus?.max_applications_per_day || 10} applications today
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-border/50 bg-card shadow-sm">
          <div className="flex flex-col gap-2 border-b border-border/60 px-6 py-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-foreground">Jobs</h2>
              <p className="text-sm text-muted-foreground">{jobs.length} results in the current queue.</p>
            </div>
            <div className="text-xs font-medium text-muted-foreground">
              Sorted by latest ingestion
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-background-subtle text-xs uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-6 py-3 text-left">Job Title</th>
                  <th className="px-6 py-3 text-left">Company</th>
                  <th className="px-6 py-3 text-left">Platform</th>
                  <th className="px-6 py-3 text-left">Score</th>
                  <th className="px-6 py-3 text-left">Status</th>
                  <th className="px-6 py-3 text-left">Date</th>
                  <th className="px-6 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-6 text-center text-muted-foreground">
                      No jobs found. Run a scan to populate the queue.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.id} className="group transition-colors duration-300 hover:bg-background-subtle">
                      <td className="px-6 py-4">
                        <div className="font-medium text-foreground">{job.title}</div>
                        <div className="text-xs text-muted-foreground">{job.location}</div>
                      </td>
                      <td className="px-6 py-4 text-foreground">{job.company}</td>
                      <td className="px-6 py-4 text-foreground uppercase">{job.platform}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="font-semibold text-foreground">{job.match_score}</div>
                          <div className="h-2 w-20 rounded-full bg-secondary">
                            <div
                              className="h-2 rounded-full bg-primary"
                              style={{ width: `${job.match_score}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${getStatusStyles(
                            job.status
                          )}`}
                        >
                          {job.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {formatDate(job.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-3 text-xs font-medium">
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="link-hover text-foreground transition-colors duration-300 hover:text-primary"
                          >
                            View Job
                          </a>
                          {job.status === 'proposal_generated' || job.status === 'applied' ? (
                            <button
                              onClick={() => handleViewProposal(job.id)}
                              className="link-hover text-accent-2-vivid"
                            >
                              View Proposal
                            </button>
                          ) : job.status === 'new' ? (
                            <button
                              onClick={() => onGenerateProposal(job.id)}
                              className="link-hover text-accent-3-vivid"
                            >
                              Generate
                            </button>
                          ) : null}
                          {job.status !== 'applied' && (
                            <button
                              onClick={() => onMarkJobApplied(job.id)}
                              className="link-hover text-green-600 hover:text-green-700"
                            >
                              Mark as Applied
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {showProposalModal && proposal && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4">
          <div className="absolute inset-0 bg-foreground/20 backdrop-blur-sm" aria-hidden="true" />
          <div className="relative mt-16 w-full max-w-2xl overflow-hidden rounded-2xl bg-background shadow-2xl">
            <div className="border-b border-border/60 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-2xl font-semibold text-foreground">Generated Proposal</h3>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Job ID: {proposal.job_id} · Generated: {formatDate(proposal.generated_at)}
                  </p>
                </div>
                <button
                  onClick={() => setShowProposalModal(false)}
                  className="rounded-full bg-secondary px-3 py-1 text-sm text-foreground transition-colors duration-300 hover:bg-border-subtle"
                  aria-label="Close proposal"
                >
                  Close
                </button>
              </div>
            </div>
            <div className="max-h-[60vh] overflow-y-auto p-6">
              <div className="rounded-lg border border-border/60 bg-background-subtle p-4 text-sm text-foreground whitespace-pre-wrap">
                {proposal.content}
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 border-t border-border/60 p-6">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(proposal.content);
                  alert('Proposal copied to clipboard!');
                }}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-all duration-300 hover:shadow-lg"
              >
                Copy to Clipboard
              </button>
              <button
                onClick={() => setShowProposalModal(false)}
                className="rounded-lg border-2 border-primary px-4 py-2 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {showLogsModal && logs && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4">
          <div className="absolute inset-0 bg-foreground/20 backdrop-blur-sm" aria-hidden="true" />
          <div className="relative mt-16 w-full max-w-4xl overflow-hidden rounded-2xl bg-background shadow-2xl">
            <div className="border-b border-border/60 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-2xl font-semibold text-foreground">LLM Job Search Logs</h3>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Clean high-level logging from the last job search
                  </p>
                </div>
                <button
                  onClick={() => setShowLogsModal(false)}
                  className="rounded-full bg-secondary px-3 py-1 text-sm text-foreground transition-colors duration-300 hover:bg-border-subtle"
                  aria-label="Close logs"
                >
                  Close
                </button>
              </div>
            </div>
            <div className="max-h-[60vh] overflow-y-auto p-6">
              <div className="rounded-lg border border-border/60 bg-background-subtle p-4 text-sm text-foreground font-mono whitespace-pre-wrap">
                {logs.logs || 'No logs available'}
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 border-t border-border/60 p-6">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(logs.logs || '');
                  alert('Logs copied to clipboard!');
                }}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-all duration-300 hover:shadow-lg"
              >
                Copy Logs
              </button>
              <button
                onClick={() => setShowLogsModal(false)}
                className="rounded-lg border-2 border-primary px-4 py-2 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ title, value, accent }) => {
  return (
    <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm transition-all duration-300 hover:border-border hover:shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-tight text-muted-foreground">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-foreground">{value}</p>
        </div>
        <div className={`h-12 w-12 rounded-full ${accent}`} />
      </div>
    </div>
  );
};

export default Dashboard;
