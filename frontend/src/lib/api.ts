export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

export type ExistingModel = "pure_svd" | "m1" | "implicit_als";

export interface Artist {
  item_id: string;
  name: string;
  url: string;
  picture_url: string;
  listeners: number;
}

export interface Recommendation extends Artist {
  rank: number;
  score: number;
  reason: string;
}

export interface RecommendResponse {
  model_version: string;
  branch: "existing_user" | "new_user" | "popularity";
  model: string;
  fallback_used: boolean;
  fallback_reason: string | null;
  ignored_item_ids: string[];
  mean_listeners: number | null;
  recommendations: Recommendation[];
}

export interface UserSummary {
  user_id: string;
  history_size: number;
}

export interface HistoryItem extends Artist {
  listening_count: number;
  split: "train" | "validation";
}

export interface UserHistory {
  user_id: string;
  total: number;
  items: HistoryItem[];
}

export class ApiError extends Error {}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new ApiError(`Không kết nối được API tại ${API_URL}. Backend đã chạy chưa?`);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(`API trả lỗi ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  users: () => call<UserSummary[]>("/users?limit=2000"),
  history: (userId: string, limit = 15) =>
    call<UserHistory>(`/users/${encodeURIComponent(userId)}/history?limit=${limit}`),
  artists: (q: string, limit = 12) =>
    call<Artist[]>(`/artists?q=${encodeURIComponent(q)}&limit=${limit}`),
  recommend: (body: {
    user_id?: string;
    history?: { item_id: string }[];
    k: number;
    model?: ExistingModel;
    m1_lambda?: number;
    m1_beta?: number;
  }) =>
    call<RecommendResponse>("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
