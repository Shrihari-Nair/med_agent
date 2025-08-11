import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, Shield, ShieldAlert, X } from 'lucide-react';

export interface SafetyBadgeProps {
  level: 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK';
  className?: string;
}

const riskConfig = {
  LOW_RISK: {
    icon: Shield,
    color: 'bg-green-100 text-green-800 border-green-200',
    label: 'Low Risk'
  },
  MODERATE_RISK: {
    icon: AlertTriangle,
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    label: 'Moderate Risk'
  },
  HIGH_RISK: {
    icon: ShieldAlert,
    color: 'bg-red-100 text-red-800 border-red-200',
    label: 'High Risk'
  }
};

export function SafetyBadge({ level, className }: SafetyBadgeProps) {
  const config = riskConfig[level];
  const Icon = config.icon;

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium border rounded-full',
      config.color,
      className
    )}>
      <Icon className="h-3.5 w-3.5" />
      {config.label}
    </div>
  );
}

export interface WarningBadgeProps {
  severity: 'mild' | 'moderate' | 'severe' | 'life_threatening' | 'contraindicated';
  className?: string;
  children: React.ReactNode;
}

const severityConfig = {
  mild: {
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: null
  },
  moderate: {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: AlertTriangle
  },
  severe: {
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: AlertTriangle
  },
  life_threatening: {
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: X
  },
  contraindicated: {
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: X
  }
};

export function WarningBadge({ severity, className, children }: WarningBadgeProps) {
  const config = severityConfig[severity];
  const Icon = config.icon;

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2.5 py-1 text-sm font-medium border rounded-full',
      config.color,
      className
    )}>
      {Icon && <Icon className="h-3.5 w-3.5" />}
      {children}
    </div>
  );
}

export interface RecommendationBadgeProps {
  strength: 'Highly Recommended' | 'Recommended' | 'Consider' | 'Not Recommended';
  className?: string;
}

const recommendationConfig = {
  'Highly Recommended': {
    color: 'bg-green-100 text-green-800 border-green-200',
    label: 'Highly Recommended'
  },
  'Recommended': {
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    label: 'Recommended'
  },
  'Consider': {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    label: 'Consider'
  },
  'Not Recommended': {
    color: 'bg-red-100 text-red-800 border-red-200',
    label: 'Not Recommended'
  }
};

export function RecommendationBadge({ strength, className }: RecommendationBadgeProps) {
  const config = recommendationConfig[strength];

  return (
    <div className={cn(
      'inline-flex items-center px-2.5 py-1 text-sm font-medium border rounded-full',
      config.color,
      className
    )}>
      {config.label}
    </div>
  );
} 