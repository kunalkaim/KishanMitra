import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-charcoal-100 overflow-hidden">
        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className={`p-3 rounded-xl ${isDestructive ? 'bg-rose-50 text-rose-600' : 'bg-saffron-50 text-saffron-600'}`}>
              <AlertTriangle className="w-6 h-6" />
            </div>
            <button
              onClick={onCancel}
              className="text-charcoal-400 hover:text-charcoal-600 p-1 rounded-lg hover:bg-charcoal-50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <h3 className="mt-4 text-lg font-bold text-forest-900">{title}</h3>
          <p className="mt-2 text-sm text-charcoal-500 leading-relaxed">{message}</p>
        </div>

        <div className="px-6 py-4 bg-charcoal-50/60 border-t border-charcoal-100 flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-semibold text-charcoal-600 hover:text-charcoal-800 rounded-xl hover:bg-charcoal-100 transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-5 py-2 text-sm font-semibold text-white rounded-xl shadow-sm transition-all active:scale-95 ${
              isDestructive
                ? 'bg-rose-600 hover:bg-rose-700'
                : 'bg-forest-900 hover:bg-forest-800'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};
