import MiniStat from './ui/MiniStat';

const OperationsSection = ({ schedulerStatus, statusCounts, onToggleAutoApply }) => {
  return (
    <section className="mt-8 grid gap-4 lg:grid-cols-2">
      <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-foreground">Operations</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Core automation controls and daily apply limits.
        </p>
        <div className="mt-4 grid gap-3 text-sm">
          <div className="flex items-center justify-between rounded-lg border border-border/60 bg-background-subtle p-3">
            <span className="text-muted-foreground">Scheduler</span>
            <span className="font-medium text-foreground">
              {schedulerStatus?.running ? 'Running' : 'Stopped'}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border/60 bg-background-subtle p-3">
            <span className="text-muted-foreground">Active Scan</span>
            <span className="font-medium text-foreground">
              {schedulerStatus?.scanning ? 'In progress' : 'Idle'}
            </span>
          </div>
          <label className="flex items-center justify-between rounded-lg border border-border/60 bg-background-subtle p-3">
            <span className="font-medium text-foreground">Auto-apply</span>
            <input
              type="checkbox"
              checked={schedulerStatus?.auto_apply_enabled || false}
              onChange={(e) => onToggleAutoApply(e.target.checked)}
              className="h-5 w-5 accent-primary"
            />
          </label>
          <div className="rounded-lg border border-border/60 bg-background-subtle p-3 text-muted-foreground">
            {schedulerStatus?.applications_today || 0} / {schedulerStatus?.max_applications_per_day || 10} applications today
          </div>
        </div>
      </div>
      <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-foreground">Pipeline Overview</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Snapshot of the current queue by status.
        </p>
        <div className="mt-4 grid gap-3">
          <MiniStat label="New" value={statusCounts.new || 0} accent="bg-secondary" />
          <MiniStat label="Proposal Generated" value={statusCounts.proposal_generated || 0} accent="bg-accent-1" />
          <MiniStat label="Manual Review" value={statusCounts.manual_review || 0} accent="bg-accent-3" />
          <MiniStat label="Applied" value={statusCounts.applied || 0} accent="bg-accent-2" />
          <MiniStat label="Failed" value={statusCounts.failed || 0} accent="bg-destructive/10" />
          <MiniStat label="Filtered" value={statusCounts.filtered || 0} accent="bg-secondary" />
        </div>
      </div>
    </section>
  );
};

export default OperationsSection;
