import { Link } from "react-router-dom";
import type { Product } from "../types";

export function ProductCard({ product }: { product: Product }) {
  const totalStock = product.inventory.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <Link className="product-card" to={`/products/${product.product_id}`}>
      <div className="product-image-wrap">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        <span className="card-bow" aria-hidden="true">୨୧</span>
        <span className={`stock-pill ${totalStock === 0 ? "sold-out" : ""}`}>
          {totalStock === 0 ? "Sold out" : "In stock"}
        </span>
      </div>
      <div className="product-card-copy">
        <span className="eyebrow">{product.garment_type}</span>
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        <div className="product-card-footer">
          <strong>${product.price.toFixed(2)}</strong>
          <span>View piece <span aria-hidden="true">→</span></span>
        </div>
      </div>
    </Link>
  );
}
