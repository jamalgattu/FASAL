import React from "react";
import { farmerService } from "../../services/farmerService";
import { ProduceListing, ListingStatus } from "../../types";
import { Card, LinkButton, PageHeader, StatusBadge, GradeBadge, EmptyState } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

const FILTERS: { label: string; value: ListingStatus | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Available", value: "available" },
  { label: "Matched", value: "matched" },
  { label: "In Order", value: "in_order" },
  { label: "Sold Out", value: "sold_out" },
];

export default function MyListings() {
  const [listings, setListings] = React.useState<ProduceListing[]>([]);
  const [filter, setFilter] = React.useState<ListingStatus | "all">("all");
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    farmerService.getListings().then((l) => {
      setListings(l);
      setLoading(false);
    });
  }, []);

  const filtered = filter === "all" ? listings : listings.filter((l) => l.status === filter);

  return (
    <div>
      <PageHeader
        title="My Listings"
        description="All produce you have listed for sale."
        action={<LinkButton to="/farmer/add-produce">+ Add Produce</LinkButton>}
      />

      <div className="flex gap-2 overflow-x-auto no-scrollbar mb-4">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`whitespace-nowrap px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filter === f.value
                ? "bg-green-700 text-white border-green-700"
                : "bg-white text-stone-600 border-stone-300 hover:bg-stone-50"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No listings in this category" />
      ) : (
        <div className="space-y-3">
          {filtered.map((l) => (
            <Card key={l.id} className="p-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <GradeBadge grade={l.qualityGrade} />
                  <div className="min-w-0">
                    <p className="font-semibold text-stone-900 truncate">
                      {l.crop} <span className="font-normal text-stone-500">— {l.variety}</span>
                    </p>
                    <p className="text-sm text-stone-500">
                      {formatQty(l.quantity, l.unit)} · {formatINR(l.expectedPrice)}/{l.unit}
                      {l.quantitySold > 0 && (
                        <span className="text-stone-400"> · {formatQty(l.quantitySold, l.unit)} sold</span>
                      )}
                    </p>
                  </div>
                </div>
                <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-1 text-sm">
                  <StatusBadge status={l.status} />
                  <span className="text-xs text-stone-400">Harvest {formatDate(l.harvestDate)}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
