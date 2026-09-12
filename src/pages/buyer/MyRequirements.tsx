import React from "react";
import { buyerService } from "../../services/buyerService";
import { BuyerRequirement } from "../../types";
import { Card, LinkButton, PageHeader, StatusBadge, EmptyState } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function MyRequirements() {
  const [requirements, setRequirements] = React.useState<BuyerRequirement[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    buyerService.getRequirements().then((r) => {
      setRequirements(r);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="My Requirements"
        description="Requirements you have posted for procurement."
        action={<LinkButton to="/buyer/post-requirement">+ Post Requirement</LinkButton>}
      />

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : requirements.length === 0 ? (
        <EmptyState title="No requirements posted yet" action={<LinkButton to="/buyer/post-requirement">+ Post Requirement</LinkButton>} />
      ) : (
        <div className="space-y-3">
          {requirements.map((r) => (
            <Card key={r.id} className="p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <p className="font-semibold text-stone-900">
                    {r.crop} <span className="font-normal text-stone-500">— {r.variety}</span>
                  </p>
                  <p className="text-sm text-stone-500 mt-0.5">
                    {formatQty(r.requiredQuantity, r.unit)} · Grade {r.requiredQuality} or better · up to {formatINR(r.acceptablePrice)}/{r.unit}
                  </p>
                  <p className="text-xs text-stone-400 mt-1">
                    Deliver to {r.deliveryLocation.district}, {r.deliveryLocation.state} by {formatDate(r.requiredDeliveryDate)}
                  </p>
                </div>
                <StatusBadge status={r.status} />
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
