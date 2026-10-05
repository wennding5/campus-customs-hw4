export interface InventoryItem {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: InventoryItem[];
}

export interface AuthUser {
  id: number;
  first_name: string | null;
  last_name: string | null;
  name: string;
  email: string;
  created_at: string;
}

export interface RegisterData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PageContext {
  path: string;
  product_id?: string;
}

export interface ChatProduct {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  price: number;
  image_url: string;
  stock_by_size: Array<InventoryItem & { in_stock: boolean }>;
  total_stock: number;
  reason: string;
}

export interface ChatResponse {
  reply: string;
  products: ChatProduct[];
  needs_clarification: boolean;
  follow_up_question: string | null;
}

export interface StoredChatMessage extends ChatHistoryMessage {
  id: number;
  products: ChatProduct[];
  created_at: string;
}
