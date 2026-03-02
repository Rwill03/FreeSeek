import StatCard from './ui/StatCard';

const StatsSection = ({ stats }) => {
  return (
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
  );
};

export default StatsSection;
