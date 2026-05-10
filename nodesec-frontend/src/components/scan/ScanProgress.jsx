import { motion } from 'framer-motion';
import { Search, Globe, Shield, Wifi, Lock, AlertTriangle, CheckCircle } from 'lucide-react';

const PHASE_ICONS = {
  subdomain_discovery: Search,
  dns: Globe,
  ports: Wifi,
  ssl: Lock,
  breach: AlertTriangle,
  analysis: Shield,
};

export default function ScanProgress({ events }) {
  const phases = events.filter((e) => e.event === 'progress');

  if (phases.length === 0) {
    return (
      <div className="flex items-center gap-3 py-12 justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
        >
          <Search size={24} className="text-accent-cyan" />
        </motion.div>
        <span className="text-text-muted">Initializing scan...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3 py-4">
      {phases.map((phase, i) => {
        const Icon = PHASE_ICONS[phase.data.phase] || Shield;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center gap-3 px-4 py-2 bg-bg-tertiary rounded-card border border-border"
          >
            <Icon size={16} className="text-accent-cyan" />
            <div className="flex-1">
              <span className="text-sm text-text-primary">{phase.data.message || `Running ${phase.data.phase}...`}</span>
              {phase.data.subdomains && (
                <span className="ml-2 text-xs text-text-muted">
                  Found {phase.data.subdomains.length} subdomains
                </span>
              )}
              {phase.data.open_ports && (
                <span className="ml-2 text-xs text-text-muted">
                  {phase.data.open_ports.length > 0
                    ? `Open ports: ${phase.data.open_ports.join(', ')}`
                    : 'No open ports found'}
                </span>
              )}
            </div>
            <CheckCircle size={14} className="text-green-safe" />
          </motion.div>
        );
      })}
    </div>
  );
}