import { impactData } from "../data/mockData";
import { ImpactDashboardData } from "../types";

const delay = <T,>(data: T, ms = 150): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

export const analyticsService = {
  // NOTE: All figures are simulated/demo data for the MVP. Forecasting
  // metrics will later be produced by an AI demand-forecasting model;
  // everything else will be computed from real transaction data.
  getImpactDashboard(): Promise<ImpactDashboardData> {
    return delay(impactData);
  },
};
