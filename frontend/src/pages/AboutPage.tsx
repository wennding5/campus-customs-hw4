import { Link } from "react-router-dom";

export function AboutPage() {
  return (
    <>
      <section className="about-hero">
        <div className="page-width about-hero-inner">
          <span className="about-bow" aria-hidden="true">୨୧</span>
          <span className="eyebrow ribbon-label">Our New Haven story</span>
          <h1>Campus spirit should feel personal.</h1>
          <p>
            We bring Yale tradition into pieces that fit real life—late library nights, crisp fall games, reunions, and proud family visits.
          </p>
        </div>
      </section>

      <section className="about-story page-width">
        <div className="about-number">01</div>
        <div>
          <span className="eyebrow">Why we’re here</span>
          <h2>Something for every part of Yale.</h2>
        </div>
        <p>
          Campus Customs is built around the communities that make the university feel like home. Our collection celebrates schools, residential colleges, teams, families, and the simple Yale classics that travel far beyond campus.
        </p>
      </section>

      <section className="about-cards page-width">
        <article>
          <span aria-hidden="true">୨୧</span>
          <h3>Community first</h3>
          <p>We design the shop around the people, traditions, and small groups that give campus its character.</p>
        </article>
        <article>
          <span aria-hidden="true">✦</span>
          <h3>Easy to find</h3>
          <p>Clear details and inventory by size make it simple to discover the right piece without the guesswork.</p>
        </article>
        <article>
          <span aria-hidden="true">♡</span>
          <h3>Made to remember</h3>
          <p>The best campus gear becomes part of your story, long after the semester or final whistle.</p>
        </article>
      </section>

      <section className="about-cta page-width">
        <div>
          <span className="eyebrow">Find your piece</span>
          <h2>Your Yale story is already in progress.</h2>
        </div>
        <Link className="button" to="/products">Explore the collection</Link>
      </section>
    </>
  );
}
