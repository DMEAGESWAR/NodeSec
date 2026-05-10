import ChainCard from './ChainCard';
import RiskScore from './RiskScore';
import EmptyState from '../ui/EmptyState';

export default function RiskPanel({ chains, overallScore, onViewPath, onSeeFixes }) {
  if (!chains || chains.length === 0) {
    return (
      <div className="bg-bg-secondary border border-border rounded-card p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
        <div className="flex justify-center mb-4">
          <RiskScore score={overallScore || 0} />
        </div>
        <EmptyState
          title="No attack chains detected"
          description="No exploitable attack paths were found. This domain looks well-configured."
        />
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Risk Analysis</h3>
        <RiskScore score={overallScore || 0} />
      </div>
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
        {chains.map((chain) => (
          <ChainCard
            key={chain.id || chain.rule_id}
            chain={chain}
            onViewPath={() => onViewPath?.(chain)}
            onSeeFixes={() => onSeeFixes?.(chain)}
          />
        ))}
      </div>
    </div>
  );
}