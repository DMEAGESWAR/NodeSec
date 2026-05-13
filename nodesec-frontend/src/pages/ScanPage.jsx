import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { addDomain, listDomains, verifyDomain } from '../api/domains';
import { startScan, getScanResult } from '../api/scan';
import PageWrapper from '../components/layout/PageWrapper';
import DomainInput from '../components/scan/DomainInput';
import ScanProgress from '../components/scan/ScanProgress';
import Card from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';
import useSSE from '../hooks/useSSE';

// Helper: extract a readable string from axios errors (handles Pydantic v2 array details)
function extractError(err) {
  const detail = err.response?.data?.detail;
  if (!detail) return err.message || 'An error occurred';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg || String(d)).join(', ');
  return String(detail);
}

export default function ScanPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [scanId, setScanId] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [adding, setAdding] = useState(false);
  const navigatedRef = useRef(false);

  // Pre-filled from dashboard "Scan" button
  const prefilledDomain = searchParams.get('domainName') || '';
  const prefilledDomainId = searchParams.get('domainId') || '';
  const autoDemo = searchParams.get('demo') === '1';

  const { data: domains } = useQuery({ queryKey: ['domains'], queryFn: listDomains });

  // Auto-trigger demo if ?demo=1
  useEffect(() => {
    if (autoDemo && !scanning) {
      handleDemo();
    }
  }, [autoDemo]);
  const { events, done: sseDone } = useSSE(scanId, !!scanId);

  const completeEvent = events.find((e) => e.event === 'complete');

  // Navigate to result — use useEffect so it never fires during render
  useEffect(() => {
    if (completeEvent && scanId && !navigatedRef.current) {
      navigatedRef.current = true;
      setTimeout(() => navigate(`/result/${scanId}`), 600);
    }
  }, [completeEvent, scanId, navigate]);

  // Fallback poller: if SSE misses the complete event (real scans can take a while),
  // poll the result endpoint every 5s until the scan is done, then navigate.
  useEffect(() => {
    if (!scanId || !scanning || navigatedRef.current) return;

    const interval = setInterval(async () => {
      if (navigatedRef.current) { clearInterval(interval); return; }
      try {
        const result = await getScanResult(scanId);
        if (result.status === 'completed' || result.status === 'failed') {
          clearInterval(interval);
          if (!navigatedRef.current) {
            navigatedRef.current = true;
            navigate(`/result/${scanId}`);
          }
        }
      } catch {
        // scan not ready yet, keep polling
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [scanId, scanning, navigate]);

  const handleDomain = async (domain) => {
    setAdding(true);
    navigatedRef.current = false;
    try {
      let domainObj;
      try {
        domainObj = await addDomain(domain);
      } catch (err) {
        if (err.response?.status === 409) {
          const existing = domains?.find((d) => d.domain_name === domain);
          if (existing) {
            domainObj = existing;
          } else {
            throw err;
          }
        } else {
          throw err;
        }
      }

      // Auto-verify so scan can proceed
      if (!domainObj.verified) {
        await verifyDomain(domainObj.id);
      }

      const result = await startScan(domainObj.id, false);
      setScanId(result.scan_id);
      setScanning(true);
      setAdding(false);
      toast.success('Scan started!');
    } catch (err) {
      setAdding(false);
      toast.error(extractError(err));
    }
  };

  const handleDemo = async () => {
    navigatedRef.current = false;
    setAdding(true);
    try {
      let domain;
      try {
        domain = await addDomain('democollege.edu');
      } catch (err) {
        if (err.response?.status === 409) {
          const existing = domains?.find((d) => d.domain_name === 'democollege.edu');
          if (existing) { domain = existing; } else { throw err; }
        } else { throw err; }
      }
      const result = await startScan(domain.id, true);
      setScanId(result.scan_id);
      setScanning(true);
      setAdding(false);
    } catch (err) {
      setAdding(false);
      toast.error('Failed to start demo scan');
    }
  };

  if (scanning) {
    return (
      <PageWrapper title="Scan in Progress">
        <Card className="mb-6">
          <ScanProgress events={events} />
          {!completeEvent && (
            <div className="flex items-center gap-2 justify-center pt-4 text-text-muted text-sm">
              <Spinner size="sm" />
              <span>Scanning... this may take up to 60 seconds for real domains</span>
            </div>
          )}
          {completeEvent && (
            <div className="text-center pt-4 text-green-safe font-medium">
              Scan complete! Redirecting to results...
            </div>
          )}
        </Card>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper title="New Scan">
      <Card className="mb-6">
        <DomainInput
          onSubmit={handleDomain}
          onDemo={handleDemo}
          isLoading={adding}
          defaultValue={prefilledDomain}
        />
        <p className="text-xs text-text-muted mt-3">
          Enter any domain to scan. NodeSec only uses passive data collection — no requests are sent directly to the target.
        </p>
      </Card>
    </PageWrapper>
  );
}
