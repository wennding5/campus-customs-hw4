import { useEffect, useRef } from "react";
import type { ChatProduct, Product } from "../types";
import { ProductCard } from "./ProductCard";

interface ChatSearchResultsProps {
  products: ChatProduct[];
  onClear: () => void;
}

function asProduct(match: ChatProduct): Product {
  return {
    product_id: match.product_id,
    name: match.name,
    garment_type: match.garment_type,
    description: match.description,
    colors: match.colors,
    search_tags: [],
    image_url: match.image_url,
    price: match.price,
    inventory: match.stock_by_size.map(({ size, quantity }) => ({ size, quantity })),
  };
}

export function ChatSearchResults({ products, onClear }: ChatSearchResultsProps) {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    sectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [products]);

  return (
    <section className="chat-results-section page-width" ref={sectionRef} aria-live="polite">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Found by your concierge</span>
          <h2>Your chat picks</h2>
          <p>These matches come directly from the Campus Customs catalogue.</p>
        </div>
        <button className="clear-results" type="button" onClick={onClear}>Clear results</button>
      </div>
      <div className="product-grid">
        {products.map((match) => (
          <ProductCard key={match.product_id} product={asProduct(match)} />
        ))}
      </div>
    </section>
  );
}
