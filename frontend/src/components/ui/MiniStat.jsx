const MiniStat = ({ label, value, accent }) => {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/60 bg-background-subtle px-4 py-2 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="flex items-center gap-2 font-medium text-foreground">
        <span className={`h-2.5 w-2.5 rounded-full ${accent}`} />
        {value}
      </span>
    </div>
  );
};

export default MiniStat;
