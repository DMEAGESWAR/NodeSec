import { useEffect, useState } from 'react';

function getScoreColor(score) {
  if (score >= 75) return 'var(--red-critical)';
  if (score >= 50) return 'var(--amber-high)';
  if (score >= 25) return '#58A6FF';
  return 'var(--green-safe)';
}

function getScoreLabel(score) {
  if (score >= 75) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 25) return 'Medium';
  return 'Low';
}

export default function RiskScore({ score, size = 'md' }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    const duration = 800;
    const start = performance.now();

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(score * eased));
      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
  }, [score]);

  const color = getScoreColor(score);
  const radius = size === 'sm' ? 24 : 36;
  const strokeWidth = size === 'sm' ? 3 : 4;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center relative" role="status" aria-label={`Risk score: ${score}`}>
      <svg width={(radius + strokeWidth) * 2} height={(radius + strokeWidth) * 2} className="transform -rotate-90">
        <circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
        />
      </svg>
      <div
        className="absolute inset-0 flex flex-col items-center justify-center"
      >
        <span className={`font-bold ${size === 'sm' ? 'text-lg' : 'text-xl'}`} style={{ color }}>
          {displayScore}
        </span>
        <span className="text-[10px] text-text-muted">{getScoreLabel(score)}</span>
      </div>
    </div>
  );
}