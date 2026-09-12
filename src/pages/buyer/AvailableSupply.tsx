import React from "react";
import { buyerService } from "../../services/buyerService";
import { ProduceListing } from "../../types";
import { Card, PageHeader, GradeBadge, EmptyState, Button, inputClass } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function AvailableSupply() {
  const [listings, setListings] = React.useState<ProduceListing[]>([]);
  const [cropFilter, setCropFilter] = React.useState("all");
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    buyerService.getAvailableSupply().then((l) => {
      setListings(l);
      setLoading(false);
    });
  }, []);

  const crops = ["all", ...Array.from(new Set(listings.map((l) => l.crop)))];
  const filtered = cropFilter === "all" ? listings : listings.filter((l) => l.crop === cropFilter);

  return (
    <div>
      <PageHeader title="Available Supply" description="Produce currently available from farmers and FPOs." />

      {!loading && (
        <div className="mb-4">
          <select className={`${inputClass} max-w-xs`} value={cropFilter} onChange={(e) => setCropFilter(e.target.value)}>
            {crops.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All crops" : c}
              </option>
            ))}
          </select>
        </div>
      )}

      {loading ? (
        <div className="grid sm:grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No supply matches this filter" />
      ) : (
        <div className="grid sm:grid-cols-2 gap-3">
          {filtered.map((l) => (
            <Card key={l.id} className="p-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-stone-900">
                    {l.crop} <span className="font-normal text-stone-500">— {l.variety}</span>
                  </p>
                  <p className="text-sm text-stone-500 mt-0.5">{l.farmerName}</p>
                </div>
                <GradeBadge grade={l.qualityGrade} />
              </div>
              <div className="mt-3 text-sm text-stone-600 space-y-1">
                <p>{formatQty(l.quantity, l.unit)} available · {formatINR(l.expectedPrice)}/{l.unit}</p>
                <p className="text-stone-400">
                  {l.location.district}, {l.location.state} · Available {formatDate(l.availableDate)}
                </p>
              </div>
              <Button variant="secondary" className="w-full mt-3">
                Express Interest
              </Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
