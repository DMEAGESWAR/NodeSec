import { Wrench, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import FixCard from './FixCard';

export default function FixPanel({ chain, onClose }) {
  const fixes = chain?.fixes || [];

  if (!chain) return null;

  return (
    <div className="bg-bg-secondary border border-border rounded-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wrench size={18} className="text-green-safe" />
          <h3 className="font-semibold">Remediation Plan — {chain.title}</h3>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-sm">
            Close
          </button>
        )}
      </div>
      <p className="text-xs text-text-muted">{chain.explanation}</p>
      {fixes.length === 0 ? (
        <p className="text-sm text-text-muted">No specific fixes available for this chain.</p>
      ) : (
        <div className="space-y-2">
          {fixes.map((fix) => (
            <FixCard key={fix.step_number} fix={fix} />
          ))}
        </div>
      )}
    </div>
  );
}