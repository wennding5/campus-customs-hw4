import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProduct } from "../api";
import type { Product } from "../types";

export function ProductPage() {
  const { productId = "" } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedSize, setSelectedSize] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setProduct(null);
    setError("");
    getProduct(productId)
      .then((item) => {
        setProduct(item);
        setSelectedSize(item.inventory.find((stock) => stock.quantity > 0)?.size ?? "");
      })
      .catch((reason: Error) => setError(reason.message));
  }, [productId]);

  if (error) {
    return (
      <section className="empty-state page-width detail-error">
        <span aria-hidden="true">୨୧</span>
        <h1>{error}</h1>
        <Link className="button" to="/products">Back to products</Link>
      </section>
    );
  }

  if (!product) return <div className="loading-card page-width detail-loading">Loading your piece…</div>;

  const selectedInventory = product.inventory.find((item) => item.size === selectedSize);
  const totalStock = product.inventory.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <section className="product-detail page-width">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <Link to="/">Home</Link><span>/</span><Link to="/products">Products</Link><span>/</span><span>{product.name}</span>
      </nav>
      <div className="detail-grid">
        <div className="detail-image-panel">
          <span className="detail-bow" aria-hidden="true">୨୧</span>
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail-copy">
          <span className="eyebrow">{product.garment_type}</span>
          <h1>{product.name}</h1>
          <div className="detail-price">${product.price.toFixed(2)}</div>
          <p className="detail-description">{product.description}</p>

          <div className="color-list">
            <strong>Available colors</strong>
            <div className="color-tags">
              {product.colors.map((color) => <span key={color}>{color}</span>)}
            </div>
          </div>

          <fieldset className="size-picker">
            <legend>Choose a size</legend>
            <div>
              {product.inventory.map((item) => (
                <button
                  key={item.size}
                  type="button"
                  disabled={item.quantity === 0}
                  className={selectedSize === item.size ? "selected" : ""}
                  onClick={() => setSelectedSize(item.size)}
                  aria-label={`${item.size}, ${item.quantity} in stock`}
                >
                  <span>{item.size}</span>
                  <small>{item.quantity === 0 ? "Out" : `${item.quantity} left`}</small>
                </button>
              ))}
            </div>
          </fieldset>

          <button className="button add-button" type="button" disabled={!selectedSize}>
            {selectedSize ? `Add size ${selectedSize} to bag` : "Currently sold out"}
          </button>
          <p className="inventory-summary">{totalStock} pieces available across all sizes · Free local pickup</p>
          {selectedInventory && selectedInventory.quantity <= 5 && (
            <p className="low-stock">Only {selectedInventory.quantity} left in size {selectedSize}.</p>
          )}

          <div className="detail-notes">
            <div><span aria-hidden="true">✦</span><p><strong>Campus-ready</strong><br />Made for everyday Yale moments.</p></div>
            <div><span aria-hidden="true">♡</span><p><strong>Picked with care</strong><br />A thoughtful gift for every Bulldog.</p></div>
          </div>
        </div>
      </div>
    </section>
  );
}
