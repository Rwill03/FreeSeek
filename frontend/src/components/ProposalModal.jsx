import { formatDate } from '../utils/formatters';

const ProposalModal = ({ proposal, onClose }) => {
  if (!proposal) return null;

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(proposal.content);
    alert('Proposal copied to clipboard!');
  };

  return (
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
              onClick={onClose}
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
            onClick={handleCopyToClipboard}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-all duration-300 hover:shadow-lg"
          >
            Copy to Clipboard
          </button>
          <button
            onClick={onClose}
            className="rounded-lg border-2 border-primary px-4 py-2 text-sm font-medium text-primary transition-colors duration-300 hover:bg-primary/10"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProposalModal;
