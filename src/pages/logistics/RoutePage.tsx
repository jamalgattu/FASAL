import React from "react";
import { Truck, Gauge, Route as RouteIcon, TimerReset } from "lucide-react";
import { logisticsService } from "../../services/logisticsService";
import { RouteComparison } from "../../types";
import { Card, PageHeader, StatCard, ProgressBar } from "../../components/ui";
import { RouteMapSVG } from "../../components/RouteMapSVG";

export default function LogisticsRoutePage() {
  const [data, setData] = React.useState<RouteComparison | null>(null);

  React.useEffect(() => {
    logisticsService.getRouteComparison().then(setData);
  }, []);

  if (!data) {
    return <div className="h-64 rounded-xl bg-stone-100 animate-pulse" />;
  }

  const { baseline, optimized, distanceSavedKm, distanceSavedPercent, timeSavedMinutes } = data;
  const utilization = Math.round((optimized.vehicle.loadedKg / optimized.vehicle.capacityKg) * 100);

  return (
    <div>
      <PageHeader
        title="Logistics & Route Planning"
        description="Synthetic route data for demo purposes. Real optimization will use an established routing algorithm (e.g. a VRP solver), not AI."
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard label="Vehicle" value={optimized.vehicle.registrationNo} sub={optimized.vehicle.type} icon={<Truck size={18} />} accent="stone" />
        <StatCard label="Total Distance" value={`${optimized.totalDistanceKm} km`} icon={<RouteIcon size={18} />} accent="green" />
        <StatCard label="Est. Duration" value={`${Math.round(optimized.estimatedDurationMinutes / 60)}h ${optimized.estimatedDurationMinutes % 60}m`} icon={<TimerReset size={18} />} accent="blue" />
        <StatCard label="Vehicle Utilization" value={`${utilization}%`} icon={<Gauge size={18} />} accent="amber" />
      </div>

      <Card className="p-4 mb-6">
        <h2 className="text-sm font-semibold text-stone-700 mb-3">Vehicle Load</h2>
        <div className="flex items-center gap-3 text-sm text-stone-600 mb-2">
          <span>{optimized.vehicle.loadedKg.toLocaleString("en-IN")} kg loaded</span>
          <span className="text-stone-300">/</span>
          <span>{optimized.vehicle.capacityKg.toLocaleString("en-IN")} kg capacity</span>
        </div>
        <ProgressBar percent={utilization} />
      </Card>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-stone-700">Baseline Route</h2>
            <span className="text-xs px-2 py-1 rounded-full bg-stone-100 text-stone-500">Sequential, unoptimized</span>
          </div>
          <RouteMapSVG route={baseline} accent="#a8a29e" />
          <dl className="grid grid-cols-2 gap-y-1 text-sm mt-3">
            <dt className="text-stone-400">Distance</dt>
            <dd className="text-right text-stone-900 font-medium">{baseline.totalDistanceKm} km</dd>
            <dt className="text-stone-400">Duration</dt>
            <dd className="text-right text-stone-900 font-medium">{baseline.estimatedDurationMinutes} min</dd>
          </dl>
        </Card>

        <Card className="p-4 border-green-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-stone-700">Optimized Route</h2>
            <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">Combined pickups</span>
          </div>
          <RouteMapSVG route={optimized} accent="#166534" />
          <dl className="grid grid-cols-2 gap-y-1 text-sm mt-3">
            <dt className="text-stone-400">Distance</dt>
            <dd className="text-right text-stone-900 font-medium">{optimized.totalDistanceKm} km</dd>
            <dt className="text-stone-400">Duration</dt>
            <dd className="text-right text-stone-900 font-medium">{optimized.estimatedDurationMinutes} min</dd>
          </dl>
        </Card>
      </div>

      <Card className="p-4 bg-green-50 border-green-200">
        <h2 className="text-sm font-semibold text-green-800 mb-2">Comparison Summary (demo figures)</h2>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <p className="text-lg font-bold text-green-800">{distanceSavedKm} km</p>
            <p className="text-xs text-green-700">Distance saved</p>
          </div>
          <div>
            <p className="text-lg font-bold text-green-800">{distanceSavedPercent}%</p>
            <p className="text-xs text-green-700">Reduction</p>
          </div>
          <div>
            <p className="text-lg font-bold text-green-800">{timeSavedMinutes} min</p>
            <p className="text-xs text-green-700">Time saved</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
