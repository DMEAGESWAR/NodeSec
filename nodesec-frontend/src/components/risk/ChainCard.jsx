import { AlertTriangle, Eye, Wrench } from 'lucide-react';
import Badge from '../ui/Badge';
import Card from '../ui/Card';

export default function ChainCard({ chain, onViewPath, onSeeFixes }) {
  return (
    <Card className="space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <AlertTriangle
            size={16}
            style={{
              color:
                chain.severity === 'critical' ? 'var(--red-critical)' : 'var(--amber-high)',
            }}
            className="mt-0.5 shrink-0"
          />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted font-mono">{chain.rule_id}</span>
              <Badge severity={chain.severity} />
            </div>
            <h4 className="text-sm font-medium mt-1">{chain.title}</h4>
          </div>
        </div>
      </div>
      <p className="text-xs text-text-muted leading-relaxed">{chain.explanation}</p>
      <div className="flex gap-2 pt-1">
        <button
          onClick={onViewPath}
          className="flex items-center gap-1 text-xs text-accent-cyan hover:underline"
        >
          <Eye size={12} /> View Attack Path
        </button>
        <button
          onClick={onSeeFixes}
          className="flex items-center gap-1 text-xs text-green-safe hover:underline"
        >
          <Wrench size={12} /> See Fixes
        </button>
      </div>
    </Card>
  );
}