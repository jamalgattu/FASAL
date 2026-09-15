export interface SessionUser {
  id: number;
  email: string;
  fullName: string;
  phone: string | null;
  role: "farmer" | "buyer" | "admin";
}

const USER_KEY = "fasal_user";
const FARMER_ID_KEY = "fasal_farmer_id";
const BUYER_ID_KEY = "fasal_buyer_id";

export function setSession(user: SessionUser, farmerId: number | null, buyerId: number | null): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  if (farmerId != null) localStorage.setItem(FARMER_ID_KEY, String(farmerId));
  else localStorage.removeItem(FARMER_ID_KEY);
  if (buyerId != null) localStorage.setItem(BUYER_ID_KEY, String(buyerId));
  else localStorage.removeItem(BUYER_ID_KEY);
}

export function clearSession(): void {
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(FARMER_ID_KEY);
  localStorage.removeItem(BUYER_ID_KEY);
}

export function getSessionUser(): SessionUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionUser;
  } catch {
    return null;
  }
}

export function getFarmerId(): number | null {
  const raw = localStorage.getItem(FARMER_ID_KEY);
  return raw ? Number(raw) : null;
}

export function getBuyerId(): number | null {
  const raw = localStorage.getItem(BUYER_ID_KEY);
  return raw ? Number(raw) : null;
}
