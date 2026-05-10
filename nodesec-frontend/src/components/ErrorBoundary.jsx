import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('React error boundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-bg-primary p-8">
          <div className="bg-bg-secondary border border-red-critical/40 rounded-card p-8 max-w-lg w-full">
            <h2 className="text-xl font-bold text-red-critical mb-2">Something went wrong</h2>
            <p className="text-text-muted text-sm mb-4">
              A rendering error occurred. Check the browser console for details.
            </p>
            <pre className="text-xs text-text-muted bg-bg-tertiary p-3 rounded overflow-auto max-h-40 mb-4">
              {this.state.error?.message}
            </pre>
            <button
              onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = '/dashboard'; }}
              className="px-4 py-2 bg-accent-blue text-white rounded-input text-sm"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
