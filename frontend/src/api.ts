import type {
  AuthUser,
  ChatHistoryMessage,
  ChatResponse,
  PageContext,
  Product,
  RegisterData,
  StoredChatMessage,
} from "./types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string | Array<{ msg: string }> } | null;
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((item) => item.msg).join(" ")
      : body?.detail;
    throw new Error(detail || (response.status === 404 ? "Product not found" : "Something went wrong"));
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const getProducts = () => request<Product[]>("/api/products");

export const getProduct = (productId: string) =>
  request<Product>(`/api/products/${encodeURIComponent(productId)}`);

export const register = (data: RegisterData) =>
  request<{ user: AuthUser }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const login = (email: string, password: string) =>
  request<{ user: AuthUser }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const getCurrentUser = () => request<{ user: AuthUser }>("/api/auth/me");

export const logout = () => request<void>("/api/auth/logout", { method: "POST" });

export const sendChatMessage = (
  message: string,
  history: ChatHistoryMessage[],
  pageContext: PageContext,
) =>
  request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, history, page_context: pageContext }),
  });

export const getChatHistory = () =>
  request<{ messages: StoredChatMessage[] }>("/api/chat/history");
