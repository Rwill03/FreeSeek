const Header = ({ schedulerStatus, onRunScan, onRefresh, onGetLogs }) => {
  return (
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
                  onClick={onGetLogs}
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
  );
};

export default Header;
