import { FileSearch } from 'lucide-react';

export default function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <FileSearch size={48} className="text-text-muted mb-4" />
      <h3 className="text-lg font-medium text-text-primary mb-2">{title}</h3>
      <p className="text-text-muted mb-4 max-w-sm">{description}</p>
      {action}
    </div>
  );
}