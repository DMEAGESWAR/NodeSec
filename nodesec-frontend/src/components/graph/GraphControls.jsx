import { Filter } from 'lucide-react';
import Button from '../ui/Button';

const FILTERS = [
  { label: 'All', severity: null },
  { label: 'Critical', severity: 'critical' },
  { label: 'High', severity: 'high' },
  { label: 'Medium', severity: 'medium' },
  { label: 'Low', severity: 'low' },
];

export default function GraphControls({ activeFilter, onFilterChange }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <Filter size={16} className="text-text-muted" />
      <span className="text-xs text-text-muted mr-1">Filter:</span>
      {FILTERS.map((f) => (
        <button
          key={f.label}
          onClick={() => onFilterChange(f.severity)}
          className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
            activeFilter === f.severity
              ? 'bg-accent-blue text-white'
              : 'bg-bg-tertiary text-text-muted hover:text-text-primary'
          }`}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}