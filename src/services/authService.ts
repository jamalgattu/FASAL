import { api, setToken, clearToken } from "../lib/apiClient";
import { setSession, clearSession, SessionUser } from "../lib/session";

interface BackendUser {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  role: "farmer" | "buyer" | "admin";
  is_active: boolean;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: BackendUser;
}

interface BackendFarmerProfile {
  id: number;
}
interface BackendBuyerProfile {
  id: number;
}

function toSessionUser(u: BackendUser): SessionUser {
  return { id: u.id, email: u.email, fullName: u.full_name, phone: u.phone, role: u.role };
}

async function establishSession(token: string, user: BackendUser): Promise<SessionUser> {
  setToken(token);
  let farmerId: number | null = null;
  let buyerId: number | null = null;

  if (user.role === "farmer") {
    const profile = await api.get<BackendFarmerProfile>("/farmers/me");
    farmerId = profile.id;
  } else if (user.role === "buyer") {
    const profile = await api.get<BackendBuyerProfile>("/buyers/me");
    buyerId = profile.id;
  }

  const sessionUser = toSessionUser(user);
  setSession(sessionUser, farmerId, buyerId);
  return sessionUser;
}

/** `identifier` is either an email or a phone number — the login page
 * offers both as separate tabs, both landing on the same backend call. */
export async function login(identifier: string, password: string): Promise<SessionUser> {
  const form = new URLSearchParams();
  form.set("username", identifier);
  form.set("password", password);
  const res = await api.postForm<TokenResponse>("/auth/login", form);
  return establishSession(res.access_token, res.user);
}

export interface FarmerRegisterInput {
  email: string;
  password: string;
  fullName: string;
  phone?: string;
  isFpo: boolean;
  orgName?: string;
  village?: string;
  district: string;
  state: string;
  lat: number;
  lng: number;
}

export async function registerFarmer(data: FarmerRegisterInput): Promise<SessionUser> {
  const res = await api.post<TokenResponse>("/auth/register/farmer", {
    email: data.email,
    password: data.password,
    full_name: data.fullName,
    phone: data.phone || undefined,
    is_fpo: data.isFpo,
    org_name: data.orgName || undefined,
    village: data.village || undefined,
    district: data.district,
    state: data.state,
    lat: data.lat,
    lng: data.lng,
  });
  return establishSession(res.access_token, res.user);
}

export interface BuyerRegisterInput {
  email: string;
  password: string;
  fullName: string;
  phone?: string;
  buyerType: "institutional" | "wholesaler" | "retail_chain" | "processor";
  orgName: string;
  district: string;
  state: string;
  lat: number;
  lng: number;
}

export async function registerBuyer(data: BuyerRegisterInput): Promise<SessionUser> {
  const res = await api.post<TokenResponse>("/auth/register/buyer", {
    email: data.email,
    password: data.password,
    full_name: data.fullName,
    phone: data.phone || undefined,
    buyer_type: data.buyerType,
    org_name: data.orgName,
    district: data.district,
    state: data.state,
    lat: data.lat,
    lng: data.lng,
  });
  return establishSession(res.access_token, res.user);
}

export function logout(): void {
  clearToken();
  clearSession();
}

export async function restoreSession(): Promise<SessionUser | null> {
  try {
    const user = await api.get<BackendUser>("/auth/me");
    return await establishSession(localStorage.getItem("fasal_token") || "", user);
  } catch {
    logout();
    return null;
  }
}
