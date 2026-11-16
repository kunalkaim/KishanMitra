import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  subMessage?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading agricultural intelligence...',
  subMessage = 'Querying hybrid models and regional datasets',
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="relative flex items-center justify-center w-16 h-16 rounded-2xl bg-forest-50 border border-forest-100 text-forest-700 shadow-soft">
        <Loader2 className="w-8 h-8 animate-spin text-forest-700" />
      </div>
      <h3 className="mt-4 text-base font-bold text-forest-900">{message}</h3>
      {subMessage && <p className="mt-1 text-xs text-charcoal-400 max-w-sm">{subMessage}</p>}
    </div>
  );
};
