import React from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, MapPin, Truck } from "lucide-react";
import { buyerService } from "../../services/buyerService";
import { Order } from "../../types";
import { Card, PageHeader, StatusBadge, GradeBadge } from "../../components/ui";
import { OrderTimeline } from "../../components/OrderTimeline";
import { formatINR, formatQty, formatDate } from "../../utils/format";

export default function BuyerOrderDetails() {
  const { id } = useParams();
  const [order, setOrder] = React.useState<Order | null | undefined>(undefined);

  React.useEffect(() => {
    if (!id) return;
    buyerService.getOrderById(id).then(setOrder);
  }, [id]);

  if (order === undefined) {
    return <div className="h-40 rounded-xl bg-stone-100 animate-pulse" />;
  }
  if (order === null) {
    return <p className="text-stone-500">Order not found.</p>;
  }

  return (
    <div className="max-w-3xl">
      <Link to="/buyer/orders" className="inline-flex items-center gap-1.5 text-sm text-stone-500 hover:text-stone-700 mb-3">
        <ArrowLeft size={14} /> Back to Orders
      </Link>
      <PageHeader
        title={`${order.crop} — ${order.variety}`}
        description={`Order ${order.id}`}
        action={<StatusBadge status={order.status} />}
      />

      <div className="grid md:grid-cols-3 gap-4">
        <Card className="p-4 md:col-span-2">
          <h2 className="text-sm font-semibold text-stone-700 mb-3">Order Details</h2>
          <dl className="grid grid-cols-2 gap-y-3 text-sm">
            <dt className="text-stone-400">Supplier</dt>
            <dd className="text-stone-900 font-medium text-right">{order.farmerName}</dd>
            <dt className="text-stone-400">Quantity</dt>
            <dd className="text-stone-900 font-medium text-right">{formatQty(order.quantity, order.unit)}</dd>
            <dt className="text-stone-400">Agreed Price</dt>
            <dd className="text-stone-900 font-medium text-right">
              {formatINR(order.agreedPrice)}/{order.unit}
            </dd>
            <dt className="text-stone-400">Total Value</dt>
            <dd className="text-stone-900 font-semibold text-right">{formatINR(order.totalValue)}</dd>
            <dt className="text-stone-400">Quality Grade</dt>
            <dd className="text-right"><GradeBadge grade={order.qualityGrade} /></dd>
            <dt className="text-stone-400">Delivery Due</dt>
            <dd className="text-stone-900 font-medium text-right">{formatDate(order.requiredDeliveryDate)}</dd>
          </dl>

          <div className="mt-4 pt-4 border-t border-stone-100 space-y-2 text-sm">
            <p className="flex items-start gap-2 text-stone-600">
              <MapPin size={16} className="mt-0.5 text-green-700 shrink-0" />
              Pickup: {order.pickupLocation.village ? `${order.pickupLocation.village}, ` : ""}
              {order.pickupLocation.district}, {order.pickupLocation.state}
            </p>
            <p className="flex items-start gap-2 text-stone-600">
              <Truck size={16} className="mt-0.5 text-blue-700 shrink-0" />
              Delivery: {order.deliveryLocation.district}, {order.deliveryLocation.state}
            </p>
          </div>
        </Card>

        <Card className="p-4">
          <h2 className="text-sm font-semibold text-stone-700 mb-4">Status Timeline</h2>
          <OrderTimeline timeline={order.timeline} currentStatus={order.status} />
        </Card>
      </div>
    </div>
  );
}
