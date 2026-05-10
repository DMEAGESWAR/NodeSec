import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';

export default function FixCard({ fix }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(fix.command).then(() => {
      setCopied(true);
      toast.success('Command copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="bg-bg-tertiary border border-border rounded-card p-3 flex items-start gap-3">
      <span className="text-xs font-mono text-accent-cyan bg-bg-primary px-2 py-0.5 rounded shrink-0">
        {fix.step_number}
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary">{fix.description}</p>
        <div className="mt-2 bg-bg-primary rounded p-2 flex items-center gap-2">
          <code className="text-xs text-green-safe flex-1 break-all font-mono">$ {fix.command}</code>
          <button
            onClick={handleCopy}
            className="text-text-muted hover:text-text-primary shrink-0"
            aria-label="Copy command"
          >
            {copied ? <Check size={14} className="text-green-safe" /> : <Copy size={14} />}
          </button>
        </div>
      </div>
    </div>
  );
}