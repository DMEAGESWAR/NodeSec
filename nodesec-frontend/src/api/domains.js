import api from './axiosInstance';

export async function addDomain(domainName) {
  const { data } = await api.post('/api/v1/domains/add', { domain_name: domainName });
  return data;
}

export async function listDomains() {
  const { data } = await api.get('/api/v1/domains/');
  return data;
}

export async function verifyDomain(domainId) {
  const { data } = await api.post(`/api/v1/domains/${domainId}/verify`);
  return data;
}