import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Search, History, FileText } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/scan', label: 'New Scan', icon: Search },
  { path: '/history', label: 'History', icon: History },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-56 bg-bg-secondary border-r border-border flex-col hidden md:flex">
      <Link to="/dashboard" className="flex items-center gap-3 px-5 py-4 border-b border-border">
        <Shield size={24} className="text-accent-cyan" />
        <span className="font-semibold text-lg">NodeSec</span>
      </Link>
      <nav className="flex-1 py-4">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                active
                  ? 'text-accent-cyan bg-bg-tertiary border-r-2 border-accent-cyan'
                  : 'text-text-muted hover:text-text-primary hover:bg-bg-tertiary'
              }`}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}