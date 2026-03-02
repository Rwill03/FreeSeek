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

export default StatCard;
