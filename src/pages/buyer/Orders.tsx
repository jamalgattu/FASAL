import React from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { buyerService } from "../../services/buyerService";
import { Order } from "../../types";
import { Card, PageHeader, StatusBadge, EmptyState } from "../../components/ui";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function BuyerOrders() {
  const [orders, setOrders] = React.useState<Order[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    buyerService.getOrders().then((o) => {
      setOrders(o);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader title="Orders" description="Orders you have placed with farmers and FPOs." />

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 rounded-xl bg-stone-100 animate-pulse" />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <EmptyState title="No orders yet" />
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <Link key={o.id} to={`/buyer/orders/${o.id}`}>
              <Card className="p-4 flex items-center justify-between gap-3 hover:border-green-300 transition-colors">
                <div className="min-w-0">
                  <p className="font-semibold text-stone-900 truncate">
                    {o.crop} <span className="font-normal text-stone-500">— {o.variety}</span>
                  </p>
                  <p className="text-sm text-stone-500">
                    {formatQty(o.quantity, o.unit)} from {o.farmerName} · {formatINR(o.totalValue)}
                  </p>
                  <p className="text-xs text-stone-400 mt-0.5">Delivery by {formatDate(o.requiredDeliveryDate)}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <StatusBadge status={o.status} />
                  <ChevronRight size={18} className="text-stone-300" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
