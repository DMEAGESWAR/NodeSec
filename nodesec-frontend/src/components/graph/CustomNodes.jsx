import { Handle, Position } from '@xyflow/react';
import { Server, Globe, Wifi, Lock, AlertTriangle } from 'lucide-react';

const ICONS = {
  domain: Globe,
  subdomain: Server,
  port: Wifi,
  breach: AlertTriangle,
  ssl_issue: Lock,
};

const COLORS = {
  critical: { border: '#FF4444', glow: 'rgba(255,68,68,0.3)' },
  high: { border: '#F0A500', glow: 'rgba(240,165,0,0.3)' },
  medium: { border: '#58A6FF', glow: 'rgba(88,166,255,0.3)' },
  low: { border: '#3FB950', glow: 'rgba(63,185,80,0.3)' },
};

export default function CustomNodes({ data }) {
  const Icon = ICONS[data.node_type] || Globe;
  const color = COLORS[data.severity] || COLORS.low;
  const isBreach = data.node_type === 'breach';

  return (
    <div
      className={`px-3 py-2 rounded-card bg-bg-secondary border-2 text-xs min-w-[120px] ${isBreach ? 'animate-pulse' : ''}`}
      style={{
        borderColor: color.border,
        boxShadow: `0 0 8px ${color.glow}`,
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: color.border }} />
      <div className="flex items-center gap-2">
        <Icon size={14} style={{ color: color.border }} />
        <span className="text-text-primary font-medium truncate max-w-[140px]">{data.label}</span>
      </div>
      {data.ip && <div className="text-text-muted text-[10px] mt-0.5">{data.ip}{data.port ? `:${data.port}` : ''}</div>}
      <Handle type="source" position={Position.Bottom} style={{ background: color.border }} />
    </div>
  );
}