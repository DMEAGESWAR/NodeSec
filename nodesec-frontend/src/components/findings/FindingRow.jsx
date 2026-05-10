import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateFinding } from '../../api/findings';
import Badge from '../ui/Badge';
import toast from 'react-hot-toast';

const STATUS_OPTIONS = ['open', 'in_progress', 'resolved', 'verified'];

export default function FindingRow({ finding, severity = 'medium', onUpdate }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({ id, updates }) => updateFinding(id, updates),
    onSuccess: () => {
      toast.success('Finding updated');
      if (onUpdate) onUpdate();
    },
    onError: () => toast.error('Failed to update finding'),
  });

  const handleStatusChange = (newStatus) => {
    mutation.mutate({ id: finding.id, updates: { status: newStatus } });
  };

  return (
    <tr className="border-b border-border hover:bg-bg-tertiary/50 transition-colors">
      <td className="px-4 py-3">
        <select
          value={finding.status || 'open'}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="bg-bg-tertiary border border-border rounded-input text-xs px-2 py-1 text-text-primary focus:outline-none focus:border-accent-blue"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>{opt.replace('_', ' ')}</option>
          ))}
        </select>
      </td>
      <td className="px-4 py-3">
        <Badge severity={severity} />
      </td>
      <td className="px-4 py-3 text-text-primary">{finding.title || 'Untitled Finding'}</td>
      <td className="px-4 py-3 text-text-muted">{finding.assigned_to || '-'}</td>
      <td className="px-4 py-3 text-text-muted text-xs">
        {finding.created_at ? new Date(finding.created_at).toLocaleDateString() : '-'}
      </td>
    </tr>
  );
}