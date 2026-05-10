import { useState } from 'react';
import { Globe, Play, Zap } from 'lucide-react';
import Button from '../ui/Button';

export default function DomainInput({ onSubmit, onDemo, isLoading }) {
  const [domain, setDomain] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (domain.trim()) {
      onSubmit(domain.trim().toLowerCase());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
      <div className="flex-1 relative">
        <Globe size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="Enter domain (e.g., example.edu)"
          className="w-full bg-bg-tertiary border border-border rounded-input pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
          disabled={isLoading}
        />
      </div>
      <Button type="submit" disabled={isLoading || !domain.trim()} size="lg">
        <Play size={16} className="mr-2" /> Start Scan
      </Button>
      <Button type="button" variant="secondary" size="lg" onClick={onDemo} disabled={isLoading}>
        <Zap size={16} className="mr-2" /> Run Demo
      </Button>
    </form>
  );
}