import React from 'react';
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
    label?: string;
  };
  variant?: 'forest' | 'saffron' | 'neutral' | 'emerald';
  badge?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'forest',
  badge,
  onClick,
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'forest':
        return {
          bg: 'bg-white',
          border: 'border-forest-100 hover:border-forest-300',
          iconBg: 'bg-forest-50 text-forest-700',
          accent: 'text-forest-900',
        };
      case 'saffron':
        return {
          bg: 'bg-white',
          border: 'border-saffron-100 hover:border-saffron-300',
          iconBg: 'bg-saffron-50 text-saffron-700',
          accent: 'text-forest-900',
        };
      case 'emerald':
        return {
          bg: 'bg-white',
          border: 'border-emerald-100 hover:border-emerald-300',
          iconBg: 'bg-emerald-50 text-emerald-700',
          accent: 'text-emerald-950',
        };
      default:
        return {
          bg: 'bg-white',
          border: 'border-charcoal-100 hover:border-charcoal-200',
          iconBg: 'bg-charcoal-50 text-charcoal-700',
          accent: 'text-charcoal-900',
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div
      onClick={onClick}
      className={`relative p-5 rounded-2xl border transition-all duration-200 shadow-soft hover:shadow-soft-lg ${styles.bg} ${styles.border} ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold tracking-wider uppercase text-charcoal-400">
            {title}
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-2xl lg:text-3xl font-extrabold tracking-tight ${styles.accent}`}>
              {value}
            </span>
            {badge && (
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-saffron-100 text-saffron-800 border border-saffron-200">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="mt-1 text-xs text-charcoal-500 font-medium">{subtitle}</p>
          )}
        </div>

        <div className={`p-3 rounded-xl ${styles.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {trend && (
        <div className="mt-4 pt-3 border-t border-charcoal-50 flex items-center gap-1.5 text-xs font-medium">
          <span
            className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded-md font-semibold ${
              trend.isPositive
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-rose-50 text-rose-700'
            }`}
          >
            {trend.isPositive ? (
              <ArrowUpRight className="w-3.5 h-3.5" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5" />
            )}
            {trend.value}
          </span>
          {trend.label && (
            <span className="text-charcoal-400">{trend.label}</span>
          )}
        </div>
      )}
    </div>
  );
};
