// =====================================================================
// FARMER SERVICE — mock implementation.
// Every function returns a Promise so that swapping the body for a
// real `fetch('/api/...')` call later requires no change to callers.
// =====================================================================
import {
  produceListings,
  allRequirements,
  matches,
  orders,
  CURRENT_FARMER_ID,
  CURRENT_FARMER_NAME,
} from "../data/mockData";
import { FarmerMatchView, FarmerStats, Order, ProduceListing } from "../types";

const delay = <T,>(data: T, ms = 150): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

export const farmerService = {
  getCurrentFarmer() {
    return delay({ id: CURRENT_FARMER_ID, name: CURRENT_FARMER_NAME });
  },

  getListings(): Promise<ProduceListing[]> {
    return delay(produceListings.filter((l) => l.farmerId === CURRENT_FARMER_ID));
  },

  getListingById(id: string): Promise<ProduceListing | undefined> {
    return delay(produceListings.find((l) => l.id === id));
  },

  // In the real API this would POST the new listing and return the
  // created record (with server-generated id/status/createdAt).
  createListing(
    input: Omit<ProduceListing, "id" | "farmerId" | "farmerName" | "isFPO" | "status" | "quantitySold" | "createdAt">
  ): Promise<ProduceListing> {
    const newListing: ProduceListing = {
      ...input,
      id: `pl-${Math.random().toString(36).slice(2, 8)}`,
      farmerId: CURRENT_FARMER_ID,
      farmerName: CURRENT_FARMER_NAME,
      isFPO: true,
      status: "available",
      quantitySold: 0,
      createdAt: new Date().toISOString(),
    };
    produceListings.unshift(newListing);
    return delay(newListing, 300);
  },

  getStats(): Promise<FarmerStats> {
    const mine = produceListings.filter((l) => l.farmerId === CURRENT_FARMER_ID);
    const myOrders = orders.filter((o) => o.farmerId === CURRENT_FARMER_ID);
    const myMatches = matches.filter((m) => mine.some((l) => l.id === m.listingId));
    const stats: FarmerStats = {
      availableProduceCount: mine.filter((l) => l.status === "available" || l.status === "matched").length,
      activeBuyerMatches: myMatches.length,
      pendingOrders: myOrders.filter((o) => o.status === "pending_confirmation" || o.status === "confirmed" || o.status === "in_transit").length,
      completedSales: myOrders.filter((o) => o.status === "delivered").length,
      totalQuantitySold: mine.reduce((sum, l) => sum + l.quantitySold, 0),
      totalQuantitySoldUnit: "kg",
      totalEarnings: myOrders.filter((o) => o.status === "delivered").reduce((sum, o) => sum + o.totalValue, 0),
    };
    return delay(stats);
  },

  getMatchesForMyListings(): Promise<FarmerMatchView[]> {
    const mine = produceListings.filter((l) => l.farmerId === CURRENT_FARMER_ID);
    const result: FarmerMatchView[] = matches
      .filter((m) => mine.some((l) => l.id === m.listingId))
      .map((m) => ({
        ...m,
        requirement: allRequirements.find((r) => r.id === m.requirementId)!,
      }))
      .filter((m) => !!m.requirement);
    return delay(result);
  },

  getOrders(): Promise<Order[]> {
    return delay(orders.filter((o) => o.farmerId === CURRENT_FARMER_ID));
  },

  getOrderById(id: string): Promise<Order | undefined> {
    return delay(orders.find((o) => o.id === id && o.farmerId === CURRENT_FARMER_ID));
  },
};
