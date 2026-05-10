import api from './axiosInstance';

export async function getScanHistory(domainId) {
  const { data } = await api.get(`/api/v1/scan/history/${domainId}`);
  return data;
}