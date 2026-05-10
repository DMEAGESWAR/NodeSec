import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { icon: Clock, color: 'text-text-muted', label: 'Pending' },
  running: { icon: Loader, color: 'text-accent-cyan', label: 'Running', animate: true },
  completed: { icon: CheckCircle, color: 'text-green-safe', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-critical', label: 'Failed' },
};

export default function ScanStatus({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-2 ${config.color}`}>
      <Icon size={16} className={config.animate ? 'animate-spin' : ''} />
      <span className="text-sm font-medium">{config.label}</span>
    </div>
  );
}