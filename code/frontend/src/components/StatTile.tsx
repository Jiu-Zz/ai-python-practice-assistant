type StatTileProps = {
  label: string;
  value: string | number;
  tone?: "green" | "orange" | "blue" | "red";
};

export function StatTile({ label, value, tone = "green" }: StatTileProps) {
  return (
    <div className={`stat-tile ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
