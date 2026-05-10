export default function Card({ children, className = '', onClick }) {
  const clickable = onClick ? 'cursor-pointer hover:border-accent-blue transition-colors' : '';
  return (
    <div
      className={`bg-bg-secondary border border-border rounded-card p-4 ${clickable} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}