import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProducts } from "../api";
import { ProductCard } from "../components/ProductCard";
import type { Product } from "../types";

export function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    getProducts().then((items) => setProducts(items.slice(0, 4))).catch(() => setProducts([]));
  }, []);

  return (
    <>
      <section className="hero page-width">
        <div className="hero-copy">
          <span className="collection-note">New Haven · Collection No. 26</span>
          <span className="eyebrow ribbon-label">Made for your Yale chapter</span>
          <h1>Wear your story.<br /><em>Keep it close.</em></h1>
          <p>
            Thoughtful Yale layers for class days, game days, family weekends, and every memory in between.
          </p>
          <div className="hero-actions">
            <Link className="button" to="/products">Shop the collection</Link>
            <Link className="text-link" to="/about">Meet Campus Customs <span>→</span></Link>
          </div>
          <div className="trust-row">
            <span><b>102</b> curated styles</span>
            <span><b>6</b> sizes per piece</span>
            <span><b>Local</b> New Haven spirit</span>
          </div>
        </div>
        <div className="hero-art" aria-label="Featured Campus Customs apparel">
          <span className="hero-seal"><b>Y</b><small>New Haven</small></span>
          <div className="pearl-orbit orbit-one" />
          <div className="pearl-orbit orbit-two" />
          {products.slice(0, 3).map((product, index) => (
            <Link
              key={product.product_id}
              className={`hero-product hero-product-${index + 1}`}
              to={`/products/${product.product_id}`}
            >
              <img src={product.image_url} alt={product.name} />
            </Link>
          ))}
          <span className="hero-bow" aria-hidden="true">୨୧</span>
        </div>
      </section>

      <section className="values-strip">
        <div><span>01</span><strong>Campus classics</strong><small>Familiar pieces, refreshed</small></div>
        <div><span>02</span><strong>Find your fit</strong><small>Inventory by size</small></div>
        <div><span>03</span><strong>Made for belonging</strong><small>Students, alumni & families</small></div>
      </section>

      <section className="section page-width">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Picked for you</span>
            <h2>Start with a classic</h2>
          </div>
          <Link className="text-link" to="/products">See all products <span>→</span></Link>
        </div>
        {products.length > 0 ? (
          <div className="product-grid featured-grid">
            {products.map((product) => <ProductCard key={product.product_id} product={product} />)}
          </div>
        ) : (
          <div className="loading-card">Start the shop API to see featured pieces.</div>
        )}
      </section>

      <section className="story-banner page-width">
        <span className="story-bow" aria-hidden="true">୨୧</span>
        <div>
          <span className="eyebrow">From New Haven, with heart</span>
          <h2>More than school colors.</h2>
        </div>
        <p>
          Campus Customs helps every corner of the Yale community find something that feels personal—from a residential college favorite to the layer you wear every Saturday.
        </p>
        <Link className="button button-light" to="/about">Our story</Link>
      </section>
    </>
  );
}
