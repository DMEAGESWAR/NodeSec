import api from './axiosInstance';

export async function getFindings(scanId) {
  const { data } = await api.get(`/api/v1/findings/${scanId}`);
  return data;
}

export async function updateFinding(findingId, updates) {
  const { data } = await api.patch(`/api/v1/findings/${findingId}`, updates);
  return data;
}