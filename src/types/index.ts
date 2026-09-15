// =====================================================================
// SHARED DOMAIN TYPES
// These interfaces are the contract the future backend API must satisfy.
// Every mock service returns data shaped exactly like this, so swapping
// mock functions for real fetch() calls later requires no UI changes.
// =====================================================================

export type Unit = "kg" | "quintal" | "tonne";

export type QualityGrade = "A" | "B" | "C";

export type ListingStatus =
  | "available"
  | "matched"
  | "in_order"
  | "sold_out"
  | "expired";

export type RequirementStatus = "open" | "matched" | "fulfilled" | "closed";

export type OrderStatus =
  | "matched"
  | "accepted"
  | "reserved"
  | "pending_confirmation"
  | "confirmed"
  | "pickup_assigned"
  | "picked_up"
  | "in_transit"
  | "delivered"
  | "completed"
  | "cancelled"
  | "rejected"
  | "partially_fulfilled"
  | "disputed";

export interface Location {
  village?: string;
  district: string;
  state: string;
  lat: number;
  lng: number;
}

// ---------------------------------------------------------------------
// FARMER / FPO SIDE
// ---------------------------------------------------------------------

export interface ProduceListing {
  id: string;
  farmerId: string;
  farmerName: string;
  isFPO: boolean;
  crop: string;
  variety: string;
  quantity: number;
  unit: Unit;
  expectedPrice: number; // per unit, in INR
  harvestDate: string; // ISO date
  availableDate: string; // ISO date
  location: Location;
  qualityGrade: QualityGrade;
  status: ListingStatus;
  quantitySold: number;
  createdAt: string;
  photos?: string[];
  notes?: string;
}

export interface FarmerStats {
  availableProduceCount: number;
  activeBuyerMatches: number;
  pendingOrders: number;
  completedSales: number;
  totalQuantitySold: number;
  totalQuantitySoldUnit: Unit;
  totalEarnings: number;
}

// ---------------------------------------------------------------------
// BUYER SIDE
// ---------------------------------------------------------------------

export interface BuyerRequirement {
  id: string;
  buyerId: string;
  buyerName: string;
  buyerType: "Institutional" | "Wholesaler" | "Retail Chain" | "Processor";
  crop: string;
  variety: string;
  requiredQuantity: number;
  unit: Unit;
  acceptablePrice: number; // max price per unit, INR
  requiredQuality: QualityGrade;
  deliveryLocation: Location;
  requiredDeliveryDate: string; // ISO date
  status: RequirementStatus;
  createdAt: string;
}

export interface BuyerStats {
  openRequirements: number;
  activeMatches: number;
  pendingOrders: number;
  completedProcurement: number;
  totalQuantityProcured: number;
  totalProcurementCost: number;
}

// ---------------------------------------------------------------------
// MATCHING
// ---------------------------------------------------------------------

export interface MatchReason {
  label: string;
  satisfied: boolean;
}

export interface Match {
  id: string;
  listingId: string;
  requirementId: string;
  matchScore: number; // 0-100
  distanceKm: number;
  reasons: MatchReason[];
  createdAt: string;
}

// Enriched match objects returned to each side's UI (denormalized for
// convenience — the real API can join these server-side).
export interface FarmerMatchView extends Match {
  requirement: BuyerRequirement;
}

export interface BuyerMatchView extends Match {
  listing: ProduceListing;
}

// ---------------------------------------------------------------------
// ORDERS
// ---------------------------------------------------------------------

export interface OrderTimelineEvent {
  status: OrderStatus;
  timestamp: string;
  note?: string;
}

export interface Order {
  id: string;
  listingId: string;
  requirementId: string;
  farmerId: string;
  farmerName: string;
  buyerId: string;
  buyerName: string;
  crop: string;
  variety: string;
  quantity: number;
  unit: Unit;
  agreedPrice: number; // per unit
  totalValue: number;
  qualityGrade: QualityGrade;
  pickupLocation: Location;
  deliveryLocation: Location;
  requiredDeliveryDate: string;
  status: OrderStatus;
  timeline: OrderTimelineEvent[];
  routeId?: string;
  createdAt: string;
}

// ---------------------------------------------------------------------
// LOGISTICS
// ---------------------------------------------------------------------

export interface RouteStop {
  id: string;
  type: "pickup" | "delivery";
  label: string;
  location: Location;
  orderId: string;
  sequence: number;
  etaMinutesFromStart: number;
}

export interface Vehicle {
  id: string;
  registrationNo: string;
  type: "Mini Truck" | "Truck" | "Refrigerated Van" | "Tempo";
  capacityKg: number;
  loadedKg: number;
}

export interface Route {
  id: string;
  vehicle: Vehicle;
  stops: RouteStop[];
  totalDistanceKm: number;
  estimatedDurationMinutes: number;
  isOptimized: boolean;
}

export interface RouteComparison {
  baseline: Route;
  optimized: Route;
  distanceSavedKm: number;
  distanceSavedPercent: number;
  timeSavedMinutes: number;
}

// ---------------------------------------------------------------------
// IMPACT ANALYTICS
// (All figures are simulated/demo data for the MVP — see UI labels.)
// ---------------------------------------------------------------------

export interface FarmerImpactMetrics {
  avgPriceRealizationIncreasePercent: number;
  totalQuantitySold: number;
  unit: Unit;
}

export interface BuyerImpactMetrics {
  avgProcurementCostChangePercent: number;
  fulfillmentRatePercent: number;
}

export interface LogisticsImpactMetrics {
  totalDistanceKm: number;
  distanceSavedKm: number;
  avgVehicleUtilizationPercent: number;
}

export interface SupplyChainImpactMetrics {
  orderFulfillmentRatePercent: number;
  wastageOrUnsoldPercent: number;
}

export interface ForecastImpactMetrics {
  predictedDemandNextWeek: number;
  unit: Unit;
  forecastErrorPercent: number;
}

export interface ImpactDashboardData {
  farmer: FarmerImpactMetrics;
  buyer: BuyerImpactMetrics;
  logistics: LogisticsImpactMetrics;
  supplyChain: SupplyChainImpactMetrics;
  forecast: ForecastImpactMetrics;
  isSimulated: true; // always true in MVP — clearly flags demo data
}
