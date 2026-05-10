import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Eye, EyeOff } from 'lucide-react';
import { useRegister } from '../hooks/useAuth';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';

export default function RegisterPage() {
  const [show, setShow] = useState(false);
  const [email, setEmail] = useState('');
  const [orgName, setOrgName] = useState('');
  const [password, setPassword] = useState('');
  const reg = useRegister();

  const handleSubmit = (e) => {
    e.preventDefault();
    reg.mutate({ email, password, org_name: orgName });
  };

  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-2">
          <div className="flex justify-center">
            <Shield size={40} className="text-accent-cyan" />
          </div>
          <h1 className="text-2xl font-bold">Create an account</h1>
          <p className="text-text-muted text-sm">Get started with NodeSec</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              className="w-full bg-bg-tertiary border border-border rounded-input px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
            />
          </div>
          <div>
            <input
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              placeholder="Organization name"
              required
              className="w-full bg-bg-tertiary border border-border rounded-input px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
            />
          </div>
          <div className="relative">
            <input
              type={show ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 8 characters)"
              required
              minLength={8}
              className="w-full bg-bg-tertiary border border-border rounded-input px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
            />
            <button type="button" onClick={() => setShow(!show)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted" tabIndex={-1}>
              {show ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          <Button type="submit" size="lg" className="w-full" disabled={reg.isPending}>
            {reg.isPending ? <Spinner size="sm" /> : 'Create Account'}
          </Button>
        </form>

        <p className="text-center text-sm text-text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-accent-cyan hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}