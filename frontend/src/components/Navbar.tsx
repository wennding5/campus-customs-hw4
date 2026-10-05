import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../auth";

const links = [
  ["/", "Home"],
  ["/products", "Products"],
  ["/about", "About us"],
] as const;

export function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, loading, logout } = useAuth();

  const logOut = async () => {
    await logout();
    setOpen(false);
  };

  return (
    <header className="nav-wrap">
      <nav className="navbar" aria-label="Main navigation">
        <Link className="brand" to="/" onClick={() => setOpen(false)}>
          <span className="brand-bow" aria-hidden="true"><b>Y</b><i>୨୧</i></span>
          <span className="brand-copy"><b>Campus Customs</b><small>Yale · New Haven</small></span>
        </Link>
        <button
          className="menu-button"
          type="button"
          aria-expanded={open}
          aria-controls="main-menu"
          aria-label="Toggle navigation"
          onClick={() => setOpen((value) => !value)}
        >
          <span />
          <span />
          <span />
        </button>
        <div id="main-menu" className={`nav-menu ${open ? "is-open" : ""}`}>
          <div className="nav-links">
            {links.map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                onClick={() => setOpen(false)}
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                {label}
              </NavLink>
            ))}
          </div>
          <div className="nav-actions">
            {!loading && user ? (
              <>
                <span className="account-greeting">Hi, {user.first_name || user.name}</span>
                <button className="nav-logout" type="button" onClick={logOut}>Log out</button>
              </>
            ) : (
              <>
                <NavLink to="/login" onClick={() => setOpen(false)}>Log in</NavLink>
                <NavLink className="button button-small" to="/create-account" onClick={() => setOpen(false)}>
                  Create account
                </NavLink>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
