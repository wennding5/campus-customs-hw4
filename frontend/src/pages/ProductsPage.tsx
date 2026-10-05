import { useEffect, useMemo, useState } from "react";
import { getProducts } from "../api";
import { ProductCard } from "../components/ProductCard";
import type { Product } from "../types";

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All pieces");
  const [size, setSize] = useState("Any size");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(
    () => ["All pieces", ...Array.from(new Set(products.map((item) => item.garment_type))).sort()],
    [products],
  );

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return products.filter((product) => {
      const matchesCategory = category === "All pieces" || product.garment_type === category;
      const matchesSize = size === "Any size" || product.inventory.some(
        (item) => item.size === size && item.quantity > 0,
      );
      const matchesStock = !inStockOnly || product.inventory.some((item) => item.quantity > 0);
      const matchesQuery = !normalized || [
        product.name,
        product.garment_type,
        product.description,
        ...product.colors,
        ...product.search_tags,
      ].join(" ").toLowerCase().includes(normalized);
      return matchesCategory && matchesSize && matchesStock && matchesQuery;
    });
  }, [category, inStockOnly, products, query, size]);

  const hasFilters = Boolean(query || category !== "All pieces" || size !== "Any size" || inStockOnly);

  const clearFilters = () => {
    setQuery("");
    setCategory("All pieces");
    setSize("Any size");
    setInStockOnly(false);
  };

  return (
    <section className="section page-width products-page">
      <div className="page-intro centered">
        <span className="eyebrow ribbon-label">The full collection</span>
        <h1>Find your Yale favorite</h1>
        <p>Browse everyday layers, spirited staples, and pieces made for your corner of campus.</p>
      </div>

      <div className="catalogue-tools">
        <label className="search-field">
          <span className="sr-only">Search products</span>
          <span aria-hidden="true">⌕</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by style, school, sport, or color"
          />
        </label>
        <label className="select-field">
          <span className="sr-only">Filter by garment type</span>
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label className="select-field">
          <span className="sr-only">Filter by available size</span>
          <select value={size} onChange={(event) => setSize(event.target.value)}>
            {['Any size', 'XS', 'S', 'M', 'L', 'XL', 'XXL'].map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label className="stock-filter">
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(event) => setInStockOnly(event.target.checked)}
          />
          In stock only
        </label>
        <span className="results-count">{filtered.length} {filtered.length === 1 ? "piece" : "pieces"}</span>
        {hasFilters && <button className="reset-filters" type="button" onClick={clearFilters}>Reset</button>}
      </div>

      {loading && <div className="loading-card">Gathering the collection…</div>}
      {error && <div className="error-card">{error}. Make sure the FastAPI server is running.</div>}
      {!loading && !error && (
        filtered.length > 0 ? (
          <div className="product-grid">
            {filtered.map((product) => <ProductCard key={product.product_id} product={product} />)}
          </div>
        ) : (
          <div className="empty-state">
            <span aria-hidden="true">୨୧</span>
            <h2>No pieces found</h2>
            <p>Try a broader search or choose another category.</p>
          </div>
        )
      )}
    </section>
  );
}
