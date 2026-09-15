import { api } from "../lib/apiClient";

interface BackendFarmer {
  id: number;
  org_name: string | null;
  full_name: string | null;
  is_fpo: boolean;
}

interface BackendBuyer {
  id: number;
  org_name: string;
  buyer_type: "Institutional" | "Wholesaler" | "Retail Chain" | "Processor";
}

const farmerCache = new Map<number, { name: string; isFpo: boolean }>();
const buyerCache = new Map<number, { name: string; buyerType: BackendBuyer["buyer_type"] }>();

export async function getFarmerDisplay(farmerId: number): Promise<{ name: string; isFpo: boolean }> {
  const cached = farmerCache.get(farmerId);
  if (cached) return cached;

  const f = await api.get<BackendFarmer>(`/farmers/${farmerId}`);
  const display = { name: f.org_name || f.full_name || "Farmer", isFpo: f.is_fpo };
  farmerCache.set(farmerId, display);
  return display;
}

export async function getBuyerDisplay(
  buyerId: number,
): Promise<{ name: string; buyerType: BackendBuyer["buyer_type"] }> {
  const cached = buyerCache.get(buyerId);
  if (cached) return cached;

  const b = await api.get<BackendBuyer>(`/buyers/${buyerId}`);
  const display = { name: b.org_name, buyerType: b.buyer_type };
  buyerCache.set(buyerId, display);
  return display;
}
