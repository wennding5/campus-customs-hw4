import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import type { RegisterData } from "../types";

interface AuthShellProps {
  mode: "login" | "create";
}

function AuthShell({ mode }: AuthShellProps) {
  const { user, loading, login, register } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const isLogin = mode === "login";

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    const form = new FormData(event.currentTarget);

    try {
      if (isLogin) {
        await login(String(form.get("email")), String(form.get("password")));
      } else {
        const data: RegisterData = {
          first_name: String(form.get("firstName")),
          last_name: String(form.get("lastName")),
          email: String(form.get("email")),
          password: String(form.get("password")),
          confirm_password: String(form.get("confirmPassword")),
        };
        if (data.password !== data.confirm_password) {
          throw new Error("Passwords do not match");
        }
        await register(data);
      }
      navigate("/products", { replace: true });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to continue");
    } finally {
      setSubmitting(false);
    }
  };

  if (!loading && user) return <Navigate to="/products" replace />;

  return (
    <section className="auth-page">
      <div className="auth-decoration" aria-hidden="true">
        <span>୨୧</span>
        <p>Yale memories,<br />made wearable.</p>
      </div>
      <div className="auth-card">
        <span className="eyebrow">{isLogin ? "Welcome back" : "Join our community"}</span>
        <h1>{isLogin ? "Log in" : "Create account"}</h1>
        <p>{isLogin ? "Your favorites are waiting." : "Save favorites and make every visit feel personal."}</p>
        <form onSubmit={submit}>
          {!isLogin && (
            <div className="form-row">
              <label>First name<input name="firstName" autoComplete="given-name" required /></label>
              <label>Last name<input name="lastName" autoComplete="family-name" required /></label>
            </div>
          )}
          <label>Email address<input type="email" name="email" autoComplete="email" required /></label>
          <label>Password<input type="password" name="password" autoComplete={isLogin ? "current-password" : "new-password"} minLength={8} required /></label>
          {!isLogin && (
            <label>Confirm password<input type="password" name="confirmPassword" autoComplete="new-password" minLength={8} required /></label>
          )}
          <button className="button auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Please wait…" : isLogin ? "Log in" : "Create my account"}
          </button>
        </form>
        {error && <p className="form-error" role="alert">{error}</p>}
        <p className="auth-switch">
          {isLogin ? "New to Campus Customs?" : "Already have an account?"}{" "}
          <Link to={isLogin ? "/create-account" : "/login"}>{isLogin ? "Create an account" : "Log in"}</Link>
        </p>
      </div>
    </section>
  );
}

export function LoginPage() {
  return <AuthShell mode="login" />;
}

export function CreateAccountPage() {
  return <AuthShell mode="create" />;
}
