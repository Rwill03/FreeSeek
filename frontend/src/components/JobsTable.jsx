import { useState, useMemo } from 'react';
import { getStatusStyles } from '../utils/styles';
import { formatDate } from '../utils/formatters';

const JobsTable = ({ jobs, onGenerateProposal, onMarkJobApplied, onViewProposal }) => {
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [minScore, setMinScore] = useState(0);
  const [sortBy, setSortBy] = useState('newest');

  const availablePlatforms = useMemo(() => {
    const platforms = jobs
      .map((job) => job.platform)
      .filter(Boolean)
      .map((platform) => platform.toLowerCase());
    return Array.from(new Set(platforms));
  }, [jobs]);

  const filteredJobs = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    const filtered = jobs.filter((job) => {
      const matchesQuery = !normalizedQuery
        || [job.title, job.company, job.location, job.platform]
          .filter(Boolean)
          .some((field) => field.toLowerCase().includes(normalizedQuery));
      const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
      const matchesPlatform = platformFilter === 'all'
        || (job.platform || '').toLowerCase() === platformFilter;
      const matchesScore = Number(job.match_score || 0) >= minScore;

      return matchesQuery && matchesStatus && matchesPlatform && matchesScore;
    });

    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === 'score_high') {
        return Number(b.match_score || 0) - Number(a.match_score || 0);
      }
      if (sortBy === 'score_low') {
        return Number(a.match_score || 0) - Number(b.match_score || 0);
      }
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    });

    return sorted;
  }, [jobs, minScore, platformFilter, query, sortBy, statusFilter]);

  const handleClearFilters = () => {
    setQuery('');
    setStatusFilter('all');
    setPlatformFilter('all');
    setMinScore(0);
    setSortBy('newest');
  };

  return (
    <section className="mt-8 rounded-2xl border border-border/50 bg-card shadow-sm">
      <div className="flex flex-col gap-4 border-b border-border/60 px-6 py-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-foreground">Jobs</h2>
          <p className="text-sm text-muted-foreground">
            Showing {filteredJobs.length} of {jobs.length} results.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-muted-foreground">
          <span>Sorted by</span>
          <select
            value={sortBy}
            onChange={(event) => setSortBy(event.target.value)}
            className="rounded-md border border-border/60 bg-background px-2 py-1 text-xs text-foreground"
          >
            <option value="newest">Newest first</option>
            <option value="score_high">Score high to low</option>
            <option value="score_low">Score low to high</option>
          </select>
        </div>
      </div>

      <div className="grid gap-3 border-b border-border/60 px-6 py-4 text-sm md:grid-cols-2 lg:grid-cols-5">
        <label className="flex flex-col gap-2">
          <span className="text-xs font-medium uppercase tracking-tight text-muted-foreground">Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Title, company, location"
            className="rounded-lg border border-border/60 bg-background px-3 py-2 text-sm text-foreground"
          />
        </label>
        <label className="flex flex-col gap-2">
          <span className="text-xs font-medium uppercase tracking-tight text-muted-foreground">Status</span>
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="rounded-lg border border-border/60 bg-background px-3 py-2 text-sm text-foreground"
          >
            <option value="all">All</option>
            <option value="new">New</option>
            <option value="proposal_generated">Proposal generated</option>
            <option value="manual_review">Manual review</option>
            <option value="applied">Applied</option>
            <option value="failed">Failed</option>
            <option value="filtered">Filtered</option>
          </select>
        </label>
        <label className="flex flex-col gap-2">
          <span className="text-xs font-medium uppercase tracking-tight text-muted-foreground">Platform</span>
          <select
            value={platformFilter}
            onChange={(event) => setPlatformFilter(event.target.value)}
            className="rounded-lg border border-border/60 bg-background px-3 py-2 text-sm text-foreground"
          >
            <option value="all">All</option>
            {availablePlatforms.map((platform) => (
              <option key={platform} value={platform}>
                {platform}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-2 lg:col-span-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-tight text-muted-foreground">Min score</span>
            <span className="text-xs font-medium text-foreground">{minScore}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={minScore}
            onChange={(event) => setMinScore(Number(event.target.value))}
            className="w-full accent-primary"
          />
        </label>
        <button
          onClick={handleClearFilters}
          className="rounded-lg border-2 border-primary px-4 py-2 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
        >
          Clear Filters
        </button>
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
            {filteredJobs.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-6 text-center text-muted-foreground">
                  No jobs match the current filters.
                </td>
              </tr>
            ) : (
              filteredJobs.map((job) => (
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
                          onClick={() => onViewProposal(job.id)}
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
  );
};

export default JobsTable;
