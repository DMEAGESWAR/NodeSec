import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft } from 'lucide-react';
import { getFindings } from '../api/findings';
import PageWrapper from '../components/layout/PageWrapper';
import FindingsTable from '../components/findings/FindingsTable';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';

export default function FindingsPage() {
  const { scanId } = useParams();
  const navigate = useNavigate();

  const { data: findings, isLoading, refetch } = useQuery({
    queryKey: ['findings', scanId],
    queryFn: () => getFindings(scanId),
    enabled: !!scanId,
  });

  return (
    <PageWrapper>
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" onClick={() => navigate(`/result/${scanId}`)}>
          <ArrowLeft size={16} className="mr-1" /> Back to Results
        </Button>
        <h1 className="text-xl font-bold">Findings</h1>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : (
        <FindingsTable findings={findings} onUpdate={refetch} />
      )}
    </PageWrapper>
  );
}