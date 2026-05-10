export default function Button({ children, variant = 'primary', size = 'md', disabled, onClick, className = '', type = 'button' }) {
  const base = 'inline-flex items-center justify-center font-medium transition-colors focus:ring-2 focus:ring-accent-blue rounded-input disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-accent-blue text-white hover:bg-blue-700',
    secondary: 'bg-bg-tertiary text-text-primary border border-border hover:bg-bg-secondary',
    danger: 'bg-red-critical text-white hover:bg-red-700',
    ghost: 'text-text-muted hover:text-text-primary',
  };
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };

  return (
    <button
      type={type}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}