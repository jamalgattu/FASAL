import React from "react";
import { ClipboardList, Handshake, Clock, CheckCircle2 } from "lucide-react";
import { buyerService } from "../../services/buyerService";
import { BuyerRequirement, BuyerStats } from "../../types";
import { Card, LinkButton, PageHeader, StatCard, StatusBadge, EmptyState } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function BuyerDashboard() {
  const [stats, setStats] = React.useState<BuyerStats | null>(null);
  const [requirements, setRequirements] = React.useState<BuyerRequirement[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    Promise.all([buyerService.getStats(), buyerService.getRequirements()]).then(([s, r]) => {
      setStats(s);
      setRequirements(r.slice(0, 4));
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="Welcome back, Amrit Retail"
        description="An overview of your procurement activity."
        action={<LinkButton to="/buyer/post-requirement">+ Post Requirement</LinkButton>}
      />

      {loading || !stats ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard label="Open Requirements" value={stats.openRequirements} icon={<ClipboardList size={18} />} accent="green" />
          <StatCard label="Active Matches" value={stats.activeMatches} icon={<Handshake size={18} />} accent="blue" />
          <StatCard label="Pending Orders" value={stats.pendingOrders} icon={<Clock size={18} />} accent="amber" />
          <StatCard
            label="Completed Procurement"
            value={stats.completedProcurement}
            sub={`${formatINR(stats.totalProcurementCost)} total`}
            icon={<CheckCircle2 size={18} />}
            accent="stone"
          />
        </div>
      )}

      <div className="mt-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-stone-800">Your Requirements</h2>
          <LinkButton to="/buyer/requirements" variant="ghost">View all →</LinkButton>
        </div>

        {requirements.length === 0 ? (
          <EmptyState
            title="No requirements posted yet"
            description="Post a requirement to start receiving matches from farmers and FPOs."
            action={<LinkButton to="/buyer/post-requirement">+ Post Requirement</LinkButton>}
          />
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {requirements.map((r) => (
              <Card key={r.id} className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-stone-900">
                      {r.crop} <span className="font-normal text-stone-500">— {r.variety}</span>
                    </p>
                    <p className="text-sm text-stone-500 mt-0.5">
                      {formatQty(r.requiredQuantity, r.unit)} · up to {formatINR(r.acceptablePrice)}/{r.unit}
                    </p>
                  </div>
                  <StatusBadge status={r.status} />
                </div>
                <p className="text-xs text-stone-400 mt-3">Needed by {formatDate(r.requiredDeliveryDate)}</p>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
