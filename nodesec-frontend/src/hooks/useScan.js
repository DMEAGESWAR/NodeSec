import { useQuery } from '@tanstack/react-query';
import { getScanResult, getScanHistory } from '../api/scan';

export const QUERY_KEYS = {
  scan: (id) => ['scan', id],
  scanChains: (id) => ['scan', id, 'chains'],
  findings: (scanId) => ['findings', scanId],
  history: (domainId) => ['history', domainId],
};

export function useScanResult(scanId) {
  return useQuery({
    queryKey: QUERY_KEYS.scan(scanId),
    queryFn: () => getScanResult(scanId),
    enabled: !!scanId,
    staleTime: Infinity,
    gcTime: 30 * 60 * 1000,
  });
}

export function useScanHistory(domainId) {
  return useQuery({
    queryKey: QUERY_KEYS.history(domainId),
    queryFn: () => getScanHistory(domainId),
    enabled: !!domainId,
    staleTime: 5 * 60 * 1000,
  });
}