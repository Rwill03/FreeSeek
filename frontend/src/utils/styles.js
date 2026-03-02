/**
 * Styling utilities for job statuses
 */
export const getStatusStyles = (status) => {
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
