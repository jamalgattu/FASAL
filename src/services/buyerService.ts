// =====================================================================
// BUYER SERVICE — mock implementation. Same pattern as farmerService.
// =====================================================================
import {
  buyerRequirements,
  allListings,
  matches,
  orders,
  CURRENT_BUYER_ID,
  CURRENT_BUYER_NAME,
} from "../data/mockData";
import { BuyerMatchView, BuyerRequirement, BuyerStats, Order, ProduceListing } from "../types";

const delay = <T,>(data: T, ms = 150): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

export const buyerService = {
  getCurrentBuyer() {
    return delay({ id: CURRENT_BUYER_ID, name: CURRENT_BUYER_NAME });
  },

  getRequirements(): Promise<BuyerRequirement[]> {
    return delay(buyerRequirements.filter((r) => r.buyerId === CURRENT_BUYER_ID));
  },

  getRequirementById(id: string): Promise<BuyerRequirement | undefined> {
    return delay(buyerRequirements.find((r) => r.id === id));
  },

  createRequirement(
    input: Omit<BuyerRequirement, "id" | "buyerId" | "buyerName" | "status" | "createdAt">
  ): Promise<BuyerRequirement> {
    const newRequirement: BuyerRequirement = {
      ...input,
      id: `br-${Math.random().toString(36).slice(2, 8)}`,
      buyerId: CURRENT_BUYER_ID,
      buyerName: CURRENT_BUYER_NAME,
      status: "open",
      createdAt: new Date().toISOString(),
    };
    buyerRequirements.unshift(newRequirement);
    return delay(newRequirement, 300);
  },

  getAvailableSupply(): Promise<ProduceListing[]> {
    return delay(allListings.filter((l) => l.status === "available"));
  },

  getStats(): Promise<BuyerStats> {
    const mine = buyerRequirements.filter((r) => r.buyerId === CURRENT_BUYER_ID);
    const myMatches = matches.filter((m) => mine.some((r) => r.id === m.requirementId));
    const myOrders = orders.filter((o) => o.buyerId === CURRENT_BUYER_ID);
    const stats: BuyerStats = {
      openRequirements: mine.filter((r) => r.status === "open").length,
      activeMatches: myMatches.length,
      pendingOrders: myOrders.filter((o) => o.status === "pending_confirmation" || o.status === "confirmed" || o.status === "in_transit").length,
      completedProcurement: myOrders.filter((o) => o.status === "delivered").length,
      totalQuantityProcured: myOrders.filter((o) => o.status === "delivered").reduce((s, o) => s + o.quantity, 0),
      totalProcurementCost: myOrders.filter((o) => o.status === "delivered").reduce((s, o) => s + o.totalValue, 0),
    };
    return delay(stats);
  },

  getRecommendedMatches(): Promise<BuyerMatchView[]> {
    const mine = buyerRequirements.filter((r) => r.buyerId === CURRENT_BUYER_ID);
    const result: BuyerMatchView[] = matches
      .filter((m) => mine.some((r) => r.id === m.requirementId))
      .map((m) => ({
        ...m,
        listing: allListings.find((l) => l.id === m.listingId)!,
      }))
      .filter((m) => !!m.listing)
      .sort((a, b) => b.matchScore - a.matchScore);
    return delay(result);
  },

  getOrders(): Promise<Order[]> {
    return delay(orders.filter((o) => o.buyerId === CURRENT_BUYER_ID));
  },

  getOrderById(id: string): Promise<Order | undefined> {
    return delay(orders.find((o) => o.id === id && o.buyerId === CURRENT_BUYER_ID));
  },
};
