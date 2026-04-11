type Status = string;

const dot: Record<string, string> = {
  confirmed: "bg-ok",
  cancelled:  "bg-danger",
  completed:  "bg-info",
};

export default function StatusBadge({ status }: { status: Status }) {
  const s = status?.toLowerCase() ?? "";
  const cls = `badge-${s}`;
  return (
    <span className={cls}>
      {dot[s] && <span className={`w-1.5 h-1.5 rounded-full ${dot[s]}`} />}
      {status}
    </span>
  );
}

