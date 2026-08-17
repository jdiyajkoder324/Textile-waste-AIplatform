import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./AuthLayout.css";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("Industry");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password) {
      setError("Fill in all fields to continue.");
      return;
    }
    if (password.length < 6) {
      setError("Password should be at least 6 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await register(name, email, password, role);
      navigate("/login");
    } catch (err) {
      setError(err.message || "Registration failed.");
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
            <circle className="ti-thread-line" cx="110" cy="110" r="88" stroke="#A8721E" strokeWidth="2" />
            <circle className="ti-thread-line" cx="110" cy="110" r="34" stroke="#2F6B4F" strokeWidth="2" style={{ animationDirection: "reverse" }} />
          </svg>
        </div>

        <div>
          <p className="ti-brand-quote">
            "Industry logs the batch. Recyclers find it. Nothing usable stays buried in a warehouse."
          </p>
          <div className="ti-brand-quote-attrib">— Marketplace, in one sentence</div>
        </div>
      </aside>

      <div className="ti-auth-form-side">
        <div className="ti-auth-card">
          <h1 className="ti-auth-heading">Create your account</h1>
          <p className="ti-auth-subtext">Tell us which side of the loop you're on.</p>

          {error && <div className="ti-error-banner">{error}</div>}

          <form onSubmit={handleRegister}>
            <div className="ti-field">
              <label>I am joining as</label>
              <div className="ti-role-group">
                <div
                  className={`ti-role-pill ${role === "Industry" ? "active" : ""}`}
                  onClick={() => setRole("Industry")}
                >
                  Industry
                </div>
                <div
                  className={`ti-role-pill ${role === "Recycler" ? "active" : ""}`}
                  onClick={() => setRole("Recycler")}
                >
                  Recycler
                </div>
              </div>
            </div>

            <div className="ti-field">
              <label htmlFor="name">Full name</label>
              <input
                id="name"
                type="text"
                placeholder="Jordan Reyes"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
              />
            </div>

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
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
            </div>

            <div className="ti-field">
              <label htmlFor="confirmPassword">Confirm password</label>
              <input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
              />
            </div>

            <button type="submit" className="ti-submit-btn" disabled={submitting}>
              {submitting ? "Creating account…" : "Create account"}
            </button>
          </form>

          <div className="ti-switch-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
