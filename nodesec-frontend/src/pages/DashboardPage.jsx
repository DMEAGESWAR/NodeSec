import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Zap, Shield, ChevronRight, Clock, CheckCircle, XCircle, Activity } from 'lucide-react';
import { listDomains } from '../api/domains';
import PageWrapper from '../components/layout/PageWrapper';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

function ScoreBar({ score }) {
  if (score == null) return <span className="text-xs text-text-muted">No score</span>;
  const color = score >= 75 ? 'var(--red-critical)' : score >= 50 ? 'var(--amber-high)' : score >= 25 ? '#58A6FF' : 'var(--green-safe)';
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-medium" style={{ color }}>{score}</span>
    </div>
  );
}

function StatusIcon({ status }) {
  if (status === 'completed') return <CheckCircle size={14} className="text-green-safe" />;
  if (status === 'failed') return <XCircle size={14} className="text-red-critical" />;
  if (status === 'running') return <Activity size={14} className="text-accent-cyan animate-pulse" />;
  return <Clock size={14} className="text-text-muted" />;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { data: domains, isLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: listDomains,
  });

  const totalDomains = domains?.length || 0;

  return (
    <PageWrapper title="Dashboard">
      {/* ── Stats row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <Card className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-accent-blue/20 flex items-center justify-center shrink-0">
            <Shield size={20} className="text-accent-cyan" />
          </div>
          <div>
            <div className="text-2xl font-bold">{totalDomains}</div>
            <div className="text-xs text-text-muted">Monitored Domains</div>
          </div>
        </Card>

        <Card
          className="flex items-center gap-4 cursor-pointer hover:border-accent-blue transition-colors"
          onClick={() => navigate('/scan')}
        >
          <div className="w-10 h-10 rounded-full bg-green-safe/20 flex items-center justify-center shrink-0">
            <Plus size={20} className="text-green-safe" />
          </div>
          <div>
            <div className="text-sm font-medium">New Scan</div>
            <div className="text-xs text-text-muted">Scan any domain</div>
          </div>
        </Card>

        <Card
          className="flex items-center gap-4 cursor-pointer hover:border-accent-blue transition-colors"
          onClick={() => navigate('/scan?demo=1')}
        >
          <div className="w-10 h-10 rounded-full bg-amber-high/20 flex items-center justify-center shrink-0">
            <Zap size={20} className="text-amber-high" />
          </div>
          <div>
            <div className="text-sm font-medium">Run Demo</div>
            <div className="text-xs text-text-muted">Try with sample data</div>
          </div>
        </Card>
      </div>

      {/* ── Domain list ── */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Your Domains</h2>
        <Button size="sm" onClick={() => navigate('/scan')}>
          <Plus size={14} className="mr-1" /> Add Domain
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : !domains || domains.length === 0 ? (
        <EmptyState
          title="No domains added yet"
          description="Add a domain to start monitoring its attack surface."
          action={
            <Button onClick={() => navigate('/scan')}>
              <Plus size={16} className="mr-1" /> Add Domain
            </Button>
          }
        />
      ) : (
        <div className="space-y-2">
          {domains.map((domain) => (
            <Card key={domain.id} className="p-0 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3">
                {/* Domain info */}
                <div className="flex items-center gap-3 min-w-0">
                  <Shield
                    size={16}
                    className={domain.verified ? 'text-green-safe shrink-0' : 'text-text-muted shrink-0'}
                  />
                  <div className="min-w-0">
                    <span className="text-sm font-medium truncate block">{domain.domain_name}</span>
                    <span className={`text-xs ${domain.verified ? 'text-green-safe' : 'text-amber-high'}`}>
                      {domain.verified ? 'Verified' : 'Unverified'}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0 ml-4">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => navigate(`/history/${domain.id}`)}
                  >
                    <Clock size={13} className="mr-1" /> History
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => navigate(`/scan?domainId=${domain.id}&domainName=${domain.domain_name}`)}
                  >
                    <Activity size={13} className="mr-1" /> Scan
                  </Button>
                  <ChevronRight size={16} className="text-text-muted" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
