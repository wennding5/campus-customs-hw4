import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="empty-state page-width not-found">
      <span aria-hidden="true">୨୧</span>
      <p className="eyebrow">404</p>
      <h1>This page wandered off campus.</h1>
      <Link className="button" to="/">Return home</Link>
    </section>
  );
}
