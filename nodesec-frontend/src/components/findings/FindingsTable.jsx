import FindingRow from './FindingRow';
import EmptyState from '../ui/EmptyState';

export default function FindingsTable({ findings, onUpdate }) {
  if (!findings || findings.length === 0) {
    return (
      <EmptyState
        title="No findings yet"
        description="Complete a scan to see security findings."
      />
    );
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-card overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-bg-tertiary">
            <th className="text-left px-4 py-3 text-text-muted font-medium">Status</th>
            <th className="text-left px-4 py-3 text-text-muted font-medium">Severity</th>
            <th className="text-left px-4 py-3 text-text-muted font-medium">Title</th>
            <th className="text-left px-4 py-3 text-text-muted font-medium">Assigned To</th>
            <th className="text-left px-4 py-3 text-text-muted font-medium">Created</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((finding) => (
            <FindingRow key={finding.id} finding={finding} onUpdate={onUpdate} />
          ))}
        </tbody>
      </table>
    </div>
  );
}