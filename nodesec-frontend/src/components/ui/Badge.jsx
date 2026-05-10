const SEVERITY_COLORS = {
  critical: { bg: 'rgba(255,68,68,0.15)', text: 'var(--red-critical)', border: 'var(--red-critical)' },
  high: { bg: 'rgba(240,165,0,0.15)', text: 'var(--amber-high)', border: 'var(--amber-high)' },
  medium: { bg: 'rgba(88,166,255,0.15)', text: '#58A6FF', border: '#58A6FF' },
  low: { bg: 'rgba(63,185,80,0.15)', text: 'var(--green-safe)', border: 'var(--green-safe)' },
};

export default function Badge({ severity = 'low', children, className = '' }) {
  const colors = SEVERITY_COLORS[severity] || SEVERITY_COLORS.low;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${className}`}
      style={{ backgroundColor: colors.bg, color: colors.text, border: `1px solid ${colors.border}` }}
      role="status"
    >
      {children || severity}
    </span>
  );
}

export { SEVERITY_COLORS };