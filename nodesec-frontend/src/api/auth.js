import api from './axiosInstance';

export async function registerUser({ email, password, org_name }) {
  const { data } = await api.post('/api/v1/auth/register', { email, password, org_name });
  return data;
}

export async function loginUser({ email, password }) {
  const { data } = await api.post('/api/v1/auth/login', { email, password });
  return data;
}