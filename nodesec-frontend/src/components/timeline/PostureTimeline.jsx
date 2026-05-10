import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import Card from '../ui/Card';

function ScoreChange({ oldScore, newScore }) {
  if (oldScore == null) return <span className="text-text-muted">N/A</span>;
  const diff = newScore - oldScore;
  if (diff > 0) {
    return (
      <span className="flex items-center gap-1 text-red-critical text-sm">
        <ArrowUp size={14} /> +{diff} worse
      </span>
    );
  }
  if (diff < 0) {
    return (
      <span className="flex items-center gap-1 text-green-safe text-sm">
        <ArrowDown size={14} /> {diff} better
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-text-muted text-sm">
      <Minus size={14} /> No change
    </span>
  );
}

export default function PostureTimeline({ scans }) {
  if (!scans || scans.length === 0) {
    return <p className="text-text-muted text-sm">No scan history available.</p>;
  }

  return (
    <div className="space-y-3">
      {scans.map((scan, i) => {
        const prev = scans[i + 1];
        return (
          <Card key={scan.id} className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor:
                    scan.status === 'completed' ? 'var(--green-safe)' :
                    scan.status === 'failed' ? 'var(--red-critical)' :
                    'var(--text-muted)',
                }}
              />
              <div>
                <div className="text-sm">{new Date(scan.started_at).toLocaleDateString()}</div>
                <div className="text-xs text-text-muted">{scan.status}</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-lg font-bold">{scan.overall_score ?? '-'}</div>
                <div className="text-xs text-text-muted">Score</div>
              </div>
              {prev && <ScoreChange oldScore={prev.overall_score} newScore={scan.overall_score} />}
            </div>
          </Card>
        );
      })}
    </div>
  );
}