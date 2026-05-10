import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';
import { useScanResult, QUERY_KEYS } from '../hooks/useScan';
import { useQueryClient } from '@tanstack/react-query';
import PageWrapper from '../components/layout/PageWrapper';
import AttackGraph from '../components/graph/AttackGraph';
import GraphControls from '../components/graph/GraphControls';
import RiskPanel from '../components/risk/RiskPanel';
import FixPanel from '../components/fixes/FixPanel';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import ScanStatus from '../components/scan/ScanStatus';
import Modal from '../components/ui/Modal';

export default function ResultPage() {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: scan, isLoading } = useScanResult(scanId);
  const [selectedChain, setSelectedChain] = useState(null);
  const [highlightNodes, setHighlightNodes] = useState([]);
  const [showFixes, setShowFixes] = useState(false);
  const [activeFilter, setActiveFilter] = useState(null);

  // If scan is still running when we land here, poll until it completes
  useEffect(() => {
    if (!scan || scan.status === 'completed' || scan.status === 'failed') return;
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.scan(scanId) });
    }, 3000);
    return () => clearInterval(interval);
  }, [scan, scanId, queryClient]);

  if (isLoading) {
    return (
      <PageWrapper title="Loading Results...">
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      </PageWrapper>
    );
  }

  if (!scan) {
    return (
      <PageWrapper title="Results">
        <p className="text-text-muted">Scan not found.</p>
        <Button onClick={() => navigate('/dashboard')} className="mt-4">
          <ArrowLeft size={16} className="mr-1" /> Back to Dashboard
        </Button>
      </PageWrapper>
    );
  }

  // Scan still in progress — show a waiting screen instead of blank page
  if (scan.status === 'running' || scan.status === 'pending') {
    return (
      <PageWrapper title="Scan in Progress">
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Spinner size="lg" />
          <p className="text-text-muted text-sm">Scan is running, please wait...</p>
          <p className="text-text-muted text-xs">This page will refresh automatically every 3 seconds.</p>
        </div>
      </PageWrapper>
    );
  }

  if (scan.status === 'failed') {
    return (
      <PageWrapper title="Scan Results">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} className="mr-1" /> Back
          </Button>
        </div>
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <p className="text-red-critical font-semibold text-lg">Scan Failed</p>
          <p className="text-text-muted text-sm text-center max-w-md">
            The scan encountered an error. This is usually caused by a network timeout or DNS resolution failure.
            Try scanning again.
          </p>
          <Button onClick={() => navigate('/scan')}>
            Try Again
          </Button>
        </div>
      </PageWrapper>
    );
  }

  const handleViewPath = (chain) => {
    setHighlightNodes(chain.node_ids || []);
    setSelectedChain(chain);
  };

  const handleSeeFixes = (chain) => {
    setSelectedChain(chain);
    setShowFixes(true);
  };

  const handleDownloadPDF = () => {
    const token = localStorage.getItem('token');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    window.open(`${apiUrl}/api/v1/reports/${scanId}/pdf`, '_blank');
  };

  const filteredNodes = activeFilter
    ? scan.nodes.filter((n) => n.severity === activeFilter)
    : scan.nodes;

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} className="mr-1" /> Back
          </Button>
          <h1 className="text-xl font-bold">Scan Results</h1>
          <ScanStatus status={scan.status} />
        </div>
        <Button variant="secondary" onClick={handleDownloadPDF}>
          <FileText size={16} className="mr-1" /> Export PDF
        </Button>
      </div>

      <GraphControls activeFilter={activeFilter} onFilterChange={setActiveFilter} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AttackGraph
            nodes={filteredNodes}
            edges={scan.edges}
            chains={scan.chains}
            highlightNodes={highlightNodes}
            onNodeClick={(node) => {
              setHighlightNodes([]);
              setSelectedChain(null);
            }}
          />
        </div>
        <div>
          <RiskPanel
            chains={scan.chains}
            overallScore={scan.overall_score}
            onViewPath={handleViewPath}
            onSeeFixes={handleSeeFixes}
          />
        </div>
      </div>

      {showFixes && selectedChain && (
        <div className="mt-6">
          <FixPanel chain={selectedChain} onClose={() => setShowFixes(false)} />
        </div>
      )}
    </PageWrapper>
  );
}