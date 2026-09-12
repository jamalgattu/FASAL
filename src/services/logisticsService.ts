import { baselineRoute, optimizedRoute } from "../data/mockData";
import { RouteComparison } from "../types";

const delay = <T,>(data: T, ms = 150): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

export const logisticsService = {
  // NOTE: Route optimization here is mock/demo data only. The real
  // implementation will use an established VRP/TSP optimization
  // algorithm (e.g. OR-Tools) run against live order + fleet data —
  // not AI, and not yet wired up in this MVP.
  getRouteComparison(): Promise<RouteComparison> {
    const distanceSavedKm = baselineRoute.totalDistanceKm - optimizedRoute.totalDistanceKm;
    const comparison: RouteComparison = {
      baseline: baselineRoute,
      optimized: optimizedRoute,
      distanceSavedKm,
      distanceSavedPercent: Math.round((distanceSavedKm / baselineRoute.totalDistanceKm) * 100),
      timeSavedMinutes: baselineRoute.estimatedDurationMinutes - optimizedRoute.estimatedDurationMinutes,
    };
    return delay(comparison);
  },
};
