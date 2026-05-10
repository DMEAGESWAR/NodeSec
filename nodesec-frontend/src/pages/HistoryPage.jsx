import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { listDomains } from '../api/domains';
import { getScanHistory } from '../api/scan';
import PageWrapper from '../components/layout/PageWrapper';
import PostureTimeline from '../components/timeline/PostureTimeline';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

export default function HistoryPage() {
  const { domainId } = useParams();
  const navigate = useNavigate();

  const { data: domains } = useQuery({ queryKey: ['domains'], queryFn: listDomains });
  const [selectedDomain, setSelectedDomain] = useState(domainId || null);

  const { data: scans, isLoading } = useQuery({
    queryKey: ['history', selectedDomain],
    queryFn: () => getScanHistory(selectedDomain),
    enabled: !!selectedDomain,
  });

  if (!domainId) {
    return (
      <PageWrapper title="Scan History">
        {!domains || domains.length === 0 ? (
          <EmptyState
            title="No domains added"
            description="Add a domain first to see scan history."
            action={
              <Button onClick={() => navigate('/scan')}>Add Domain</Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {domains.map((domain) => (
              <Card
                key={domain.id}
                className="cursor-pointer hover:border-accent-blue"
                onClick={() => { setSelectedDomain(domain.id); navigate(`/history/${domain.id}`); }}
              >
                <h3 className="font-medium">{domain.domain_name}</h3>
                <p className="text-xs text-text-muted mt-1">
                  {domain.verified ? 'Verified' : 'Unverified'}
                </p>
              </Card>
            ))}
          </div>
        )}
      </PageWrapper>
    );
  }

  const domain = domains?.find((d) => d.id === domainId);

  return (
    <PageWrapper>
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" onClick={() => navigate('/history')}>
          <ArrowLeft size={16} className="mr-1" /> Back
        </Button>
        <h1 className="text-xl font-bold">History — {domain?.domain_name || domainId}</h1>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : (
        <PostureTimeline scans={scans} />
      )}
    </PageWrapper>
  );
}