import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { loginUser, registerUser } from '../api/auth';
import { useAuthStore } from '../store/authStore';

// Pydantic v2 returns detail as an array of objects — extract a readable string
function extractError(err) {
  const detail = err.response?.data?.detail;
  if (!detail) return err.message || 'An error occurred';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg || String(d)).join(', ');
  return String(detail);
}

export function useLogin() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      toast.success('Logged in successfully');
      navigate('/dashboard');
    },
    onError: (err) => {
      toast.error(extractError(err));
    },
  });
}

export function useRegister() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: registerUser,
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      toast.success('Account created successfully');
      navigate('/dashboard');
    },
    onError: (err) => {
      toast.error(extractError(err));
    },
  });
}