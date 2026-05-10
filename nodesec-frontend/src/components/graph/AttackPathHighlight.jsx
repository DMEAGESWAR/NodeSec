import { ShieldAlert } from 'lucide-react';

export default function AttackPathHighlight({ nodeIds }) {
  return (
    <div className="absolute top-3 left-3 z-10 bg-bg-secondary border border-red-critical/50 rounded-card px-3 py-2 text-xs flex items-center gap-2">
      <ShieldAlert size={14} className="text-red-critical" />
      <span className="text-red-critical font-medium">Attack path highlighted</span>
      <span className="text-text-muted">({nodeIds.length} nodes)</span>
    </div>
  );
}