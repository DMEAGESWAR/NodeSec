import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Zap, Shield, ChevronRight } from 'lucide-react';
import { listDomains } from '../api/domains';
import PageWrapper from '../components/layout/PageWrapper';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { data: domains, isLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: listDomains,
  });

  return (
    <PageWrapper title="Dashboard">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-accent-blue/20 flex items-center justify-center">
            <Shield size={20} className="text-accent-cyan" />
          </div>
          <div>
            <div className="text-2xl font-bold">{domains?.length || 0}</div>
            <div className="text-xs text-text-muted">Monitored Domains</div>
          </div>
        </Card>
        <Card
          className="flex items-center gap-4 cursor-pointer hover:border-accent-blue transition-colors"
          onClick={() => navigate('/scan')}
        >
          <div className="w-10 h-10 rounded-full bg-green-safe/20 flex items-center justify-center">
            <Plus size={20} className="text-green-safe" />
          </div>
          <div>
            <div className="text-sm font-medium">New Scan</div>
            <div className="text-xs text-text-muted">Analyze a domain</div>
          </div>
        </Card>
        <Card
          className="flex items-center gap-4 cursor-pointer hover:border-accent-blue transition-colors"
          onClick={() => navigate('/scan')}
        >
          <div className="w-10 h-10 rounded-full bg-amber-high/20 flex items-center justify-center">
            <Zap size={20} className="text-amber-high" />
          </div>
          <div>
            <div className="text-sm font-medium">Run Demo</div>
            <div className="text-xs text-text-muted">Try with sample data</div>
          </div>
        </Card>
      </div>

      <h2 className="text-lg font-semibold mb-4">Your Domains</h2>
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
            <Card
              key={domain.id}
              className="flex items-center justify-between cursor-pointer hover:border-accent-blue"
              onClick={() => navigate(`/scan/${domain.id}`)}
            >
              <div className="flex items-center gap-3">
                <Shield size={16} className={domain.verified ? 'text-green-safe' : 'text-text-muted'} />
                <div>
                  <span className="text-sm font-medium">{domain.domain_name}</span>
                  <span className={`ml-2 text-xs ${domain.verified ? 'text-green-safe' : 'text-amber-high'}`}>
                    {domain.verified ? 'Verified' : 'Unverified'}
                  </span>
                </div>
              </div>
              <ChevronRight size={16} className="text-text-muted" />
            </Card>
          ))}
        </div>
      )}
    </PageWrapper>
  );
}