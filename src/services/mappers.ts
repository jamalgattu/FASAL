import { getCropNameById } from "./cropService";
import { getFarmerDisplay, getBuyerDisplay } from "./profileLookup";
import {
  ProduceListing,
  BuyerRequirement,
  Order,
  OrderTimelineEvent,
  Unit,
  QualityGrade,
  ListingStatus,
  RequirementStatus,
  OrderStatus,
} from "../types";

export interface BackendProduceListing {
  id: number;
  farmer_id: number;
  crop_id: number;
  variety: string;
  quantity: number;
  quantity_reserved: number;
  quantity_sold: number;
  available_quantity: number;
  unit: string;
  price_per_unit: number;
  quality_grade: string;
  harvest_date: string;
  available_date: string;
  village: string | null;
  district: string;
  state: string;
  lat: number;
  lng: number;
  status: string;
  notes: string | null;
  created_at: string;
}

export interface BackendBuyerRequirement {
  id: number;
  buyer_id: number;
  crop_id: number;
  variety: string;
  required_quantity: number;
  fulfilled_quantity: number;
  remaining_quantity: number;
  unit: string;
  acceptable_price: number;
  required_quality: string;
  delivery_district: string;
  delivery_state: string;
  delivery_lat: number;
  delivery_lng: number;
  required_delivery_date: string;
  status: string;
  created_at: string;
}

export interface BackendOrder {
  id: number;
  match_id: number | null;
  listing_id: number;
  requirement_id: number;
  farmer_id: number;
  buyer_id: number;
  crop_id: number;
  variety: string;
  quantity: number;
  unit: string;
  agreed_price: number;
  total_value: number;
  quality_grade: string;
  pickup_district: string;
  pickup_state: string;
  pickup_lat: number;
  pickup_lng: number;
  delivery_district: string;
  delivery_state: string;
  delivery_lat: number;
  delivery_lng: number;
  required_delivery_date: string;
  status: string;
  version: number;
  created_at: string;
}

export interface BackendOrderHistoryEntry {
  id: number;
  from_status: string | null;
  to_status: string;
  changed_by_user_id: number | null;
  note: string | null;
  created_at: string;
}

export interface BackendOrderDetail extends BackendOrder {
  history: BackendOrderHistoryEntry[];
}

export interface BackendMatch {
  id: number;
  listing_id: number;
  requirement_id: number;
  allocated_quantity: number;
  match_score: number;
  distance_km: number;
  reasons: { label: string; satisfied: boolean }[];
  status: string;
  created_at: string;
}

export async function mapListing(l: BackendProduceListing): Promise<ProduceListing> {
  const [cropName, farmerDisplay] = await Promise.all([getCropNameById(l.crop_id), getFarmerDisplay(l.farmer_id)]);
  return {
    id: String(l.id),
    farmerId: String(l.farmer_id),
    farmerName: farmerDisplay.name,
    isFPO: farmerDisplay.isFpo,
    crop: cropName,
    variety: l.variety,
    quantity: Number(l.quantity),
    unit: l.unit as Unit,
    expectedPrice: Number(l.price_per_unit),
    harvestDate: l.harvest_date,
    availableDate: l.available_date,
    location: { village: l.village ?? undefined, district: l.district, state: l.state, lat: l.lat, lng: l.lng },
    qualityGrade: l.quality_grade as QualityGrade,
    status: l.status as ListingStatus,
    quantitySold: Number(l.quantity_sold),
    createdAt: l.created_at,
    notes: l.notes ?? undefined,
  };
}

export async function mapRequirement(r: BackendBuyerRequirement): Promise<BuyerRequirement> {
  const [cropName, buyerDisplay] = await Promise.all([getCropNameById(r.crop_id), getBuyerDisplay(r.buyer_id)]);
  return {
    id: String(r.id),
    buyerId: String(r.buyer_id),
    buyerName: buyerDisplay.name,
    buyerType: buyerDisplay.buyerType,
    crop: cropName,
    variety: r.variety,
    requiredQuantity: Number(r.required_quantity),
    unit: r.unit as Unit,
    acceptablePrice: Number(r.acceptable_price),
    requiredQuality: r.required_quality as QualityGrade,
    deliveryLocation: { district: r.delivery_district, state: r.delivery_state, lat: r.delivery_lat, lng: r.delivery_lng },
    requiredDeliveryDate: r.required_delivery_date,
    status: r.status as RequirementStatus,
    createdAt: r.created_at,
  };
}

export async function mapOrder(o: BackendOrder | BackendOrderDetail): Promise<Order> {
  const [cropName, farmerDisplay, buyerDisplay] = await Promise.all([
    getCropNameById(o.crop_id),
    getFarmerDisplay(o.farmer_id),
    getBuyerDisplay(o.buyer_id),
  ]);

  const history = "history" in o ? o.history : [];
  const timeline: OrderTimelineEvent[] = history.map((h) => ({
    status: h.to_status as OrderStatus,
    timestamp: h.created_at,
    note: h.note ?? undefined,
  }));

  return {
    id: String(o.id),
    listingId: String(o.listing_id),
    requirementId: String(o.requirement_id),
    farmerId: String(o.farmer_id),
    farmerName: farmerDisplay.name,
    buyerId: String(o.buyer_id),
    buyerName: buyerDisplay.name,
    crop: cropName,
    variety: o.variety,
    quantity: Number(o.quantity),
    unit: o.unit as Unit,
    agreedPrice: Number(o.agreed_price),
    totalValue: Number(o.total_value),
    qualityGrade: o.quality_grade as QualityGrade,
    pickupLocation: { district: o.pickup_district, state: o.pickup_state, lat: o.pickup_lat, lng: o.pickup_lng },
    deliveryLocation: { district: o.delivery_district, state: o.delivery_state, lat: o.delivery_lat, lng: o.delivery_lng },
    requiredDeliveryDate: o.required_delivery_date,
    status: o.status as OrderStatus,
    timeline,
    createdAt: o.created_at,
  };
}
