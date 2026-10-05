import { useState } from "react";
import { Outlet } from "react-router-dom";
import { ChatWidget } from "./ChatWidget";
import { ChatSearchResults } from "./ChatSearchResults";
import { Navbar } from "./Navbar";
import type { ChatProduct } from "../types";

export function Layout() {
  const [chatProducts, setChatProducts] = useState<ChatProduct[]>([]);

  return (
    <div className="site-shell">
      <div className="announcement">Free local pickup · Made for the Yale community</div>
      <Navbar />
      <main>
        <Outlet />
        {chatProducts.length > 0 && (
          <ChatSearchResults products={chatProducts} onClear={() => setChatProducts([])} />
        )}
      </main>
      <footer className="site-footer">
        <div className="footer-mark" aria-hidden="true">୨୧</div>
        <div>
          <strong>Campus Customs</strong>
          <p>Yale spirit, picked with care in New Haven.</p>
        </div>
        <p className="footer-note">A course project storefront · © 2026</p>
      </footer>
      <ChatWidget onProducts={setChatProducts} />
    </div>
  );
}
