import api from './axiosInstance';

export async function startScan(domainId, isDemo = false) {
  const { data } = await api.post('/api/v1/scan/start', {
    domain_id: domainId,
    is_demo: isDemo,
  });
  return data;
}

export async function getScanResult(scanId) {
  const { data } = await api.get(`/api/v1/scan/${scanId}/result`);
  return data;
}

export async function getScanHistory(domainId) {
  const { data } = await api.get(`/api/v1/scan/history/${domainId}`);
  return data;
}