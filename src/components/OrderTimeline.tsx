import React from "react";
import { CheckCircle2, Circle, AlertTriangle } from "lucide-react";
import { OrderStatus, OrderTimelineEvent } from "../types";
import { formatDateTime } from "../utils/format";

const STAGES: { status: OrderStatus; label: string }[] = [
  { status: "matched", label: "Matched" },
  { status: "accepted", label: "Accepted" },
  { status: "reserved", label: "Reserved" },
  { status: "confirmed", label: "Confirmed" },
  { status: "pickup_assigned", label: "Pickup Assigned" },
  { status: "picked_up", label: "Picked Up" },
  { status: "in_transit", label: "In Transit" },
  { status: "delivered", label: "Delivered" },
  { status: "completed", label: "Completed" },
];

const SIDE_BRANCH_LABELS: Partial<Record<OrderStatus, string>> = {
  cancelled: "Order cancelled",
  rejected: "Order rejected",
  disputed: "Order under dispute",
  partially_fulfilled: "Partially fulfilled",
};

export function OrderTimeline({ timeline, currentStatus }: { timeline: OrderTimelineEvent[]; currentStatus: OrderStatus }) {
  const sideBranchLabel = SIDE_BRANCH_LABELS[currentStatus];
  if (sideBranchLabel) {
    const event = timeline[timeline.length - 1];
    return (
      <div className="rounded-lg bg-amber-50 text-amber-800 px-4 py-3 text-sm">
        <p className="flex items-center gap-1.5 font-medium">
          <AlertTriangle size={15} />
          {sideBranchLabel}
        </p>
        {event && <p className="text-xs text-amber-700 mt-1">{formatDateTime(event.timestamp)}</p>}
        {event?.note && <p className="text-xs text-amber-700 mt-0.5">{event.note}</p>}
      </div>
    );
  }

  const currentIndex = STAGES.findIndex((s) => s.status === currentStatus);

  return (
    <ol className="relative border-l-2 border-stone-200 ml-2.5">
      {STAGES.map((stage, i) => {
        const event = timeline.find((t) => t.status === stage.status);
        const reached = i <= currentIndex;
        return (
          <li key={stage.status} className="mb-6 last:mb-0 ml-5">
            <span
              className={`absolute -left-[11px] flex items-center justify-center w-5 h-5 rounded-full ${
                reached ? "bg-green-600 text-white" : "bg-white border-2 border-stone-300"
              }`}
            >
              {reached ? <CheckCircle2 size={14} /> : <Circle size={8} className="text-stone-300" />}
            </span>
            <p className={`text-sm font-medium ${reached ? "text-stone-900" : "text-stone-400"}`}>{stage.label}</p>
            {event && (
              <>
                <p className="text-xs text-stone-400">{formatDateTime(event.timestamp)}</p>
                {event.note && <p className="text-xs text-stone-500 mt-0.5">{event.note}</p>}
              </>
            )}
          </li>
        );
      })}
    </ol>
  );
}
