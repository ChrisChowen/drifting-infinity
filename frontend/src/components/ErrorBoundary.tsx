import { Component, type ReactNode } from "react";
import { Button } from "@/components/ui";
import { Home, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  handleGoHome = () => {
    window.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-surface-0 flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center space-y-6">
            {/* Broken orb icon */}
            <div className="relative w-20 h-20 mx-auto">
              <div className="absolute inset-0 rounded-full border-2 border-red-500/30" />
              <div className="absolute inset-3 rounded-full border border-red-400/20" />
              <div className="absolute inset-6 rounded-full bg-red-500/10 flex items-center justify-center">
                <span className="text-red-400 text-2xl">!</span>
              </div>
            </div>

            <div>
              <h1 className="text-2xl font-display font-bold text-white mb-2">
                Something went wrong
              </h1>
              <p className="text-gray-400 text-sm">
                The Armillary has encountered a rift in reality. Your progress should be safe.
              </p>
            </div>

            {this.state.error && (
              <details className="text-left">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                  Technical details
                </summary>
                <pre className="mt-2 text-xs text-red-400/70 bg-surface-1 rounded-lg p-3 overflow-auto max-h-32">
                  {this.state.error.message}
                </pre>
              </details>
            )}

            <div className="flex gap-3 justify-center">
              <Button
                variant="secondary"
                size="md"
                icon={<RefreshCw size={16} />}
                onClick={this.handleReset}
              >
                Try Again
              </Button>
              <Button
                variant="primary"
                size="md"
                icon={<Home size={16} />}
                onClick={this.handleGoHome}
              >
                Return to the Nexus
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
