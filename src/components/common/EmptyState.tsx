import React from 'react';
import { LucideIcon, Sprout } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Sprout,
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 lg:p-12 text-center bg-white rounded-2xl border border-charcoal-100 shadow-soft">
      <div className="w-14 h-14 rounded-2xl bg-forest-50 border border-forest-100 flex items-center justify-center text-forest-700 mb-4">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-lg font-bold text-forest-900">{title}</h3>
      <p className="mt-1.5 text-sm text-charcoal-400 max-w-md">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-6 inline-flex items-center px-5 py-2.5 rounded-xl font-semibold text-sm bg-forest-900 hover:bg-forest-800 text-white transition-all shadow-md active:scale-95"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
