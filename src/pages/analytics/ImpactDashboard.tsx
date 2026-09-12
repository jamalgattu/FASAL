import React from "react";
import { TrendingUp, ShoppingBag, Truck, PackageCheck, LineChart } from "lucide-react";
import { analyticsService } from "../../services/analyticsService";
import { ImpactDashboardData } from "../../types";
import { Card, PageHeader, ProgressBar } from "../../components/ui";
import { formatQty } from "../../utils/format";

function Section({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-green-700">{icon}</span>
        <h2 className="text-sm font-semibold text-stone-800">{title}</h2>
      </div>
      {children}
    </Card>
  );
}

function Metric({ label, value, positive }: { label: string; value: string; positive?: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="text-sm text-stone-500">{label}</span>
      <span className={`text-sm font-semibold ${positive === undefined ? "text-stone-900" : positive ? "text-green-700" : "text-red-600"}`}>
        {value}
      </span>
    </div>
  );
}

export default function ImpactDashboard() {
  const [data, setData] = React.useState<ImpactDashboardData | null>(null);

  React.useEffect(() => {
    analyticsService.getImpactDashboard().then(setData);
  }, []);

  if (!data) {
    return <div className="h-64 rounded-xl bg-stone-100 animate-pulse" />;
  }

  return (
    <div>
      <PageHeader
        title="Impact Analytics"
        description="These figures are simulated demo data for the prototype — not measured real-world outcomes."
      />

      <div className="mb-5 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-2.5">
        ⚠ All metrics on this page use simulated/demo data for MVP presentation purposes.
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Section icon={<TrendingUp size={18} />} title="Farmer Impact (simulated)">
          <Metric
            label="Avg. price realization change"
            value={`+${data.farmer.avgPriceRealizationIncreasePercent}%`}
            positive
          />
          <Metric label="Total quantity sold" value={formatQty(data.farmer.totalQuantitySold, data.farmer.unit)} />
        </Section>

        <Section icon={<ShoppingBag size={18} />} title="Buyer Impact (simulated)">
          <Metric
            label="Avg. procurement cost change"
            value={`${data.buyer.avgProcurementCostChangePercent}%`}
            positive={data.buyer.avgProcurementCostChangePercent < 0}
          />
          <div className="pt-2">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-stone-500">Fulfillment rate</span>
              <span className="font-semibold text-stone-900">{data.buyer.fulfillmentRatePercent}%</span>
            </div>
            <ProgressBar percent={data.buyer.fulfillmentRatePercent} color="bg-blue-600" />
          </div>
        </Section>

        <Section icon={<Truck size={18} />} title="Logistics Impact (simulated)">
          <Metric label="Total distance covered" value={`${data.logistics.totalDistanceKm} km`} />
          <Metric label="Distance saved via optimization" value={`${data.logistics.distanceSavedKm} km`} positive />
          <div className="pt-2">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-stone-500">Avg. vehicle utilization</span>
              <span className="font-semibold text-stone-900">{data.logistics.avgVehicleUtilizationPercent}%</span>
            </div>
            <ProgressBar percent={data.logistics.avgVehicleUtilizationPercent} color="bg-amber-600" />
          </div>
        </Section>

        <Section icon={<PackageCheck size={18} />} title="Supply Chain Health (simulated)">
          <div className="pt-1">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-stone-500">Order fulfillment rate</span>
              <span className="font-semibold text-stone-900">{data.supplyChain.orderFulfillmentRatePercent}%</span>
            </div>
            <ProgressBar percent={data.supplyChain.orderFulfillmentRatePercent} color="bg-green-600" />
          </div>
          <div className="pt-3">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-stone-500">Wastage / unsold quantity</span>
              <span className="font-semibold text-red-600">{data.supplyChain.wastageOrUnsoldPercent}%</span>
            </div>
            <ProgressBar percent={data.supplyChain.wastageOrUnsoldPercent} color="bg-red-500" />
          </div>
        </Section>

        <Section icon={<LineChart size={18} />} title="Demand Forecasting (simulated placeholder)">
          <Metric label="Predicted demand — next week" value={formatQty(data.forecast.predictedDemandNextWeek, data.forecast.unit)} />
          <Metric label="Forecast error" value={`±${data.forecast.forecastErrorPercent}%`} />
          <p className="text-xs text-stone-400 mt-2">
            Forecasting will later be produced by an AI demand-forecasting model trained on real transaction history. This is placeholder data only.
          </p>
        </Section>
      </div>
    </div>
  );
}
