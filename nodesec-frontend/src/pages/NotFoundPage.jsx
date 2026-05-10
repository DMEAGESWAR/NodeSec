import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import Button from '../components/ui/Button';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold text-text-muted">404</h1>
        <p className="text-lg text-text-muted">Page not found</p>
        <Link to="/dashboard">
          <Button>
            <Home size={16} className="mr-1" /> Go Home
          </Button>
        </Link>
      </div>
    </div>
  );
}