import React from "react";
import { farmerService } from "../../services/farmerService";
import { FarmerMatchView } from "../../types";
import { PageHeader, EmptyState, Button } from "../../components/ui";
import { MatchCard } from "../../components/MatchCard";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function BuyerMatches() {
  const [matches, setMatches] = React.useState<FarmerMatchView[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    farmerService.getMatchesForMyListings().then((m) => {
      setMatches(m.sort((a, b) => b.matchScore - a.matchScore));
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="Buyer Matches"
        description="Buyers whose requirements match your listed produce, ranked by fit."
      />

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : matches.length === 0 ? (
        <EmptyState title="No buyer matches yet" description="List more produce to get matched with buyers." />
      ) : (
        <div className="space-y-3">
          {matches.map((m) => (
            <MatchCard
              key={m.id}
              heading={`${m.requirement.buyerName}`}
              subheading={`Wants ${formatQty(m.requirement.requiredQuantity, m.requirement.unit)} ${m.requirement.crop} (${m.requirement.variety}), Grade ${m.requirement.requiredQuality}`}
              metaLine={`Up to ${formatINR(m.requirement.acceptablePrice)}/${m.requirement.unit} · ${m.distanceKm} km away · Needed by ${formatDate(m.requirement.requiredDeliveryDate)}`}
              score={m.matchScore}
              reasons={m.reasons}
              action={<Button className="w-full sm:w-auto">Respond to Buyer</Button>}
            />
          ))}
        </div>
      )}
    </div>
  );
}
