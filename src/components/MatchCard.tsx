import React from "react";
import { Check, X } from "lucide-react";
import { MatchReason } from "../types";
import { Card } from "./ui";

function scoreColor(score: number) {
  if (score >= 85) return "text-green-700 bg-green-50 ring-green-200";
  if (score >= 70) return "text-amber-700 bg-amber-50 ring-amber-200";
  return "text-stone-600 bg-stone-100 ring-stone-200";
}

export function MatchCard({
  heading,
  subheading,
  metaLine,
  score,
  reasons,
  action,
}: {
  heading: string;
  subheading: string;
  metaLine: string;
  score: number;
  reasons: MatchReason[];
  action?: React.ReactNode;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold text-stone-900 truncate">{heading}</p>
          <p className="text-sm text-stone-600 mt-0.5">{subheading}</p>
          <p className="text-xs text-stone-400 mt-0.5">{metaLine}</p>
        </div>
        <div className={`shrink-0 flex flex-col items-center justify-center rounded-lg px-3 py-1.5 ring-1 ${scoreColor(score)}`}>
          <span className="text-lg font-bold leading-none">{score}%</span>
          <span className="text-[10px] font-medium uppercase tracking-wide">match</span>
        </div>
      </div>

      <ul className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5">
        {reasons.map((r, i) => (
          <li key={i} className={`flex items-center gap-1.5 text-sm ${r.satisfied ? "text-stone-700" : "text-stone-400"}`}>
            {r.satisfied ? (
              <Check size={14} className="text-green-600 shrink-0" />
            ) : (
              <X size={14} className="text-red-400 shrink-0" />
            )}
            {r.label}
          </li>
        ))}
      </ul>

      {action && <div className="mt-3 pt-3 border-t border-stone-100">{action}</div>}
    </Card>
  );
}
