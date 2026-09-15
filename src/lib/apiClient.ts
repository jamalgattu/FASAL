const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";
const TOKEN_KEY = "fasal_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const isFormBody = options.body instanceof URLSearchParams;

  const headers: Record<string, string> = {
    ...(options.body && !isFormBody ? { "Content-Type": "application/json" } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1${path}`, { ...options, headers });
  } catch {
    throw new ApiError("Could not reach the server. Check your connection or try again shortly.", 0);
  }

  if (!res.ok) {
    let detail = res.statusText || "Something went wrong.";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response had no JSON body — fall back to statusText
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T,>(path: string) => request<T>(path, { method: "GET" }),
  post: <T,>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  patch: <T,>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body !== undefined ? JSON.stringify(body) : undefined }),
  postForm: <T,>(path: string, form: URLSearchParams) => request<T>(path, { method: "POST", body: form }),
};
