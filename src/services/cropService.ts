import { api } from "../lib/apiClient";

interface BackendCrop {
  id: number;
  name: string;
  default_unit: string;
}

let cache: BackendCrop[] | null = null;

async function loadCrops(): Promise<BackendCrop[]> {
  if (!cache) cache = await api.get<BackendCrop[]>("/crops/");
  return cache;
}

export async function getCropIdByName(name: string): Promise<number> {
  const crops = await loadCrops();
  const existing = crops.find((c) => c.name.toLowerCase() === name.trim().toLowerCase());
  if (existing) return existing.id;

  const created = await api.post<BackendCrop>("/crops/", { name: name.trim(), default_unit: "kg" });
  cache = [...(cache || []), created];
  return created.id;
}

export async function getCropNameById(id: number): Promise<string> {
  const crops = await loadCrops();
  return crops.find((c) => c.id === id)?.name ?? "Unknown crop";
}
