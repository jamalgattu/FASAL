import React from "react";
import { Package, Handshake, Clock, CheckCircle2, Scale } from "lucide-react";
import { farmerService } from "../../services/farmerService";
import { FarmerStats, ProduceListing } from "../../types";
import { Card, LinkButton, PageHeader, StatCard, StatusBadge, GradeBadge, EmptyState } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function FarmerDashboard() {
  const [stats, setStats] = React.useState<FarmerStats | null>(null);
  const [recentListings, setRecentListings] = React.useState<ProduceListing[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    Promise.all([farmerService.getStats(), farmerService.getListings()]).then(([s, listings]) => {
      setStats(s);
      setRecentListings(listings.slice(0, 4));
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="Namaste, Ramesh Ji 🌾"
        description="Here is a quick look at your produce and sales."
        action={<LinkButton to="/farmer/add-produce">+ Add Produce</LinkButton>}
      />

      {loading || !stats ? (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <StatCard label="Available Produce" value={stats.availableProduceCount} icon={<Package size={18} />} accent="green" />
          <StatCard label="Active Buyer Matches" value={stats.activeBuyerMatches} icon={<Handshake size={18} />} accent="blue" />
          <StatCard label="Pending Orders" value={stats.pendingOrders} icon={<Clock size={18} />} accent="amber" />
          <StatCard label="Completed Sales" value={stats.completedSales} icon={<CheckCircle2 size={18} />} accent="green" />
          <StatCard
            label="Total Quantity Sold"
            value={formatQty(stats.totalQuantitySold, stats.totalQuantitySoldUnit)}
            sub={`Earnings: ${formatINR(stats.totalEarnings)}`}
            icon={<Scale size={18} />}
            accent="stone"
          />
        </div>
      )}

      <div className="mt-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-stone-800">Your Recent Listings</h2>
          <LinkButton to="/farmer/listings" variant="ghost">View all →</LinkButton>
        </div>

        {recentListings.length === 0 ? (
          <EmptyState
            title="No produce listed yet"
            description="Add your first produce listing so buyers can find it."
            action={<LinkButton to="/farmer/add-produce">+ Add Produce</LinkButton>}
          />
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {recentListings.map((l) => (
              <Card key={l.id} className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-stone-900">
                      {l.crop} <span className="font-normal text-stone-500">— {l.variety}</span>
                    </p>
                    <p className="text-sm text-stone-500 mt-0.5">
                      {formatQty(l.quantity, l.unit)} · {formatINR(l.expectedPrice)}/{l.unit}
                    </p>
                  </div>
                  <GradeBadge grade={l.qualityGrade} />
                </div>
                <div className="flex items-center justify-between mt-3">
                  <StatusBadge status={l.status} />
                  <span className="text-xs text-stone-400">Available {formatDate(l.availableDate)}</span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
