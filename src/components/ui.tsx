import React from "react";
import { Link } from "react-router-dom";

// -----------------------------------------------------------------------
// Card
// -----------------------------------------------------------------------
export function Card({
  children,
  className = "",
  as: As = "div",
}: {
  children: React.ReactNode;
  className?: string;
  as?: any;
}) {
  return (
    <As className={`bg-white border border-stone-200 rounded-xl shadow-sm ${className}`}>
      {children}
    </As>
  );
}

// -----------------------------------------------------------------------
// StatCard — used on both dashboards
// -----------------------------------------------------------------------
export function StatCard({
  label,
  value,
  sub,
  icon,
  accent = "green",
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon?: React.ReactNode;
  accent?: "green" | "amber" | "blue" | "stone";
}) {
  const accentMap: Record<string, string> = {
    green: "bg-green-50 text-green-700",
    amber: "bg-amber-50 text-amber-700",
    blue: "bg-blue-50 text-blue-700",
    stone: "bg-stone-100 text-stone-700",
  };
  return (
    <Card className="p-4 flex items-start gap-3">
      {icon && (
        <div className={`shrink-0 rounded-lg p-2.5 ${accentMap[accent]}`} aria-hidden="true">
          {icon}
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs font-medium text-stone-500 truncate">{label}</p>
        <p className="text-xl font-semibold text-stone-900 mt-0.5">{value}</p>
        {sub && <p className="text-xs text-stone-400 mt-0.5">{sub}</p>}
      </div>
    </Card>
  );
}

// -----------------------------------------------------------------------
// Badge — status pill with a fixed color per status keyword
// -----------------------------------------------------------------------
const STATUS_STYLES: Record<string, string> = {
  available: "bg-green-100 text-green-800",
  matched: "bg-blue-100 text-blue-800",
  in_order: "bg-amber-100 text-amber-800",
  sold_out: "bg-stone-200 text-stone-600",
  expired: "bg-red-100 text-red-700",
  open: "bg-green-100 text-green-800",
  fulfilled: "bg-stone-200 text-stone-600",
  closed: "bg-stone-200 text-stone-600",
  pending_confirmation: "bg-amber-100 text-amber-800",
  confirmed: "bg-blue-100 text-blue-800",
  in_transit: "bg-indigo-100 text-indigo-800",
  delivered: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-700",
};

const STATUS_LABELS: Record<string, string> = {
  available: "Available",
  matched: "Matched",
  in_order: "In Order",
  sold_out: "Sold Out",
  expired: "Expired",
  open: "Open",
  fulfilled: "Fulfilled",
  closed: "Closed",
  pending_confirmation: "Pending Confirmation",
  confirmed: "Confirmed",
  in_transit: "In Transit",
  delivered: "Delivered",
  cancelled: "Cancelled",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
        STATUS_STYLES[status] ?? "bg-stone-100 text-stone-700"
      }`}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}

export function GradeBadge({ grade }: { grade: string }) {
  const styles: Record<string, string> = {
    A: "bg-green-100 text-green-800 border-green-200",
    B: "bg-amber-100 text-amber-800 border-amber-200",
    C: "bg-red-100 text-red-700 border-red-200",
  };
  return (
    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold border ${styles[grade] ?? ""}`}>
      {grade}
    </span>
  );
}

// -----------------------------------------------------------------------
// Button
// -----------------------------------------------------------------------
export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  className = "",
  disabled = false,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
  disabled?: boolean;
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants: Record<string, string> = {
    primary: "bg-green-700 text-white hover:bg-green-800 focus-visible:ring-green-700",
    secondary: "bg-white text-stone-800 border border-stone-300 hover:bg-stone-50 focus-visible:ring-stone-400",
    ghost: "text-stone-600 hover:bg-stone-100 focus-visible:ring-stone-400",
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </button>
  );
}

export function LinkButton({
  to,
  children,
  variant = "primary",
  className = "",
}: {
  to: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const variants: Record<string, string> = {
    primary: "bg-green-700 text-white hover:bg-green-800 focus-visible:ring-green-700",
    secondary: "bg-white text-stone-800 border border-stone-300 hover:bg-stone-50 focus-visible:ring-stone-400",
    ghost: "text-stone-600 hover:bg-stone-100 focus-visible:ring-stone-400",
  };
  return (
    <Link to={to} className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </Link>
  );
}

// -----------------------------------------------------------------------
// PageHeader
// -----------------------------------------------------------------------
export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold text-stone-900">{title}</h1>
        {description && <p className="text-sm text-stone-500 mt-1">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

// -----------------------------------------------------------------------
// EmptyState
// -----------------------------------------------------------------------
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <Card className="p-10 text-center">
      <p className="text-stone-700 font-medium">{title}</p>
      {description && <p className="text-sm text-stone-400 mt-1">{description}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </Card>
  );
}

// -----------------------------------------------------------------------
// ProgressBar
// -----------------------------------------------------------------------
export function ProgressBar({ percent, color = "bg-green-600" }: { percent: number; color?: string }) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="w-full h-2 bg-stone-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}>
      <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${clamped}%` }} />
    </div>
  );
}

// -----------------------------------------------------------------------
// Field wrapper for forms
// -----------------------------------------------------------------------
export function Field({
  label,
  children,
  hint,
  required,
}: {
  label: string;
  children: React.ReactNode;
  hint?: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-stone-700 mb-1.5">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      {children}
      {hint && <span className="block text-xs text-stone-400 mt-1">{hint}</span>}
    </label>
  );
}

export const inputClass =
  "w-full rounded-lg border border-stone-300 px-3 py-2.5 text-sm text-stone-900 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-green-600";
