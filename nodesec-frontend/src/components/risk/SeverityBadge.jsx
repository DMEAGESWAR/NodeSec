import Badge, { SEVERITY_COLORS } from '../ui/Badge';

export { SEVERITY_COLORS };
export default function SeverityBadge({ severity }) {
  return <Badge severity={severity}>{severity}</Badge>;
}