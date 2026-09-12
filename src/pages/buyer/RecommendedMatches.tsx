import React from "react";
import { buyerService } from "../../services/buyerService";
import { BuyerMatchView } from "../../types";
import { PageHeader, EmptyState, Button } from "../../components/ui";
import { MatchCard } from "../../components/MatchCard";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function RecommendedMatches() {
  const [matches, setMatches] = React.useState<BuyerMatchView[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    buyerService.getRecommendedMatches().then((m) => {
      setMatches(m);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="Recommended Matches"
        description="Farmers and FPOs whose produce best matches your requirements."
      />

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : matches.length === 0 ? (
        <EmptyState title="No matches yet" description="Post a requirement to see recommended suppliers." />
      ) : (
        <div className="space-y-3">
          {matches.map((m) => (
            <MatchCard
              key={m.id}
              heading={m.listing.farmerName}
              subheading={`${formatQty(m.listing.quantity, m.listing.unit)} ${m.listing.crop} (${m.listing.variety}), Grade ${m.listing.qualityGrade}`}
              metaLine={`${formatINR(m.listing.expectedPrice)}/${m.listing.unit} · ${m.distanceKm} km away · Available ${formatDate(m.listing.availableDate)}`}
              score={m.matchScore}
              reasons={m.reasons}
              action={<Button className="w-full sm:w-auto">Send Order Request</Button>}
            />
          ))}
        </div>
      )}
    </div>
  );
}
