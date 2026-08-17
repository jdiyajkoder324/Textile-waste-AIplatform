import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./AuthLayout.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { initiateLogin } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Enter your email and password to continue.");
      return;
    }

    setSubmitting(true);
    try {
      const data = await initiateLogin(email, password);
      navigate("/verify-otp", {
        state: {
          otp_session_id: data.otp_session_id,
          email_hint: data.email_hint,
          expires_in_seconds: data.expires_in_seconds,
        },
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="ti-auth-shell">
      <aside className="ti-auth-brand">
        <div>
          <div className="ti-brand-mark">Textile<span>Intel</span></div>
          <div className="ti-brand-tag">Waste Intelligence Platform</div>
        </div>

        <div className="ti-spool-wrap">
          <svg width="220" height="220" viewBox="0 0 220 220" fill="none">
            <circle cx="110" cy="110" r="70" stroke="#E3E1D8" strokeWidth="2" />
            <circle cx="110" cy="110" r="52" stroke="#E3E1D8" strokeWidth="2" />
            <circle className="ti-thread-line" cx="110" cy="110" r="88" stroke="#2F6B4F" strokeWidth="2" />
            <circle className="ti-thread-line" cx="110" cy="110" r="34" stroke="#A8721E" strokeWidth="2" style={{ animationDirection: "reverse" }} />
          </svg>
        </div>

        <div>
          <p className="ti-brand-quote">
            "Every batch logged here is a thread traced back into the supply chain — not landfill."
          </p>
          <div className="ti-brand-quote-attrib">— Industry Reclaim Program</div>
        </div>
      </aside>

      <div className="ti-auth-form-side">
        <div className="ti-auth-card">
          <h1 className="ti-auth-heading">Welcome back</h1>
          <p className="ti-auth-subtext">Sign in to manage your textile waste inventory.</p>

          {error && <div className="ti-error-banner">{error}</div>}

          <form onSubmit={handleLogin}>
            <div className="ti-field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className="ti-field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="ti-submit-btn" disabled={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="ti-switch-link">
            Don't have an account? <Link to="/register">Create one</Link>
          </div>
        </div>
      </div>
    </div>
  );
}