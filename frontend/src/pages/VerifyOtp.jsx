import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function VerifyOtp() {
  const navigate = useNavigate();
  const location = useLocation();
  const { completeLogin, resendLoginOtp } = useAuth();

  const sessionState = location.state;
  const [otpSessionId, setOtpSessionId] = useState(sessionState?.otp_session_id ?? null);
  const [emailHint, setEmailHint] = useState(sessionState?.email_hint ?? "");
  const [digits, setDigits] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [cooldown, setCooldown] = useState(60);
  const [expiresIn, setExpiresIn] = useState(sessionState?.expires_in_seconds ?? 300);

  const inputRefs = useRef([]);

  useEffect(() => {
    if (!sessionState?.otp_session_id) {
      navigate("/login", { replace: true });
    }
  }, [sessionState, navigate]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(t);
  }, [cooldown]);

  useEffect(() => {
    if (expiresIn <= 0) return;
    const t = setInterval(() => setExpiresIn((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [expiresIn]);

  const formatTime = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  const handleDigitChange = (index, value) => {
    if (!/^\d?$/.test(value)) return;
    const next = [...digits];
    next[index] = value;
    setDigits(next);
    if (value && index < 5) inputRefs.current[index + 1]?.focus();
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData("text").trim().slice(0, 6);
    if (!/^\d+$/.test(pasted)) return;
    e.preventDefault();
    const next = pasted.split("").concat(Array(6).fill("")).slice(0, 6);
    setDigits(next);
    inputRefs.current[Math.min(pasted.length, 5)]?.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otp = digits.join("");
    if (otp.length !== 6) {
      setError("Enter all 6 digits");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await completeLogin(otpSessionId, otp);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid OTP");
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setResendLoading(true);
    try {
      const data = await resendLoginOtp(otpSessionId);
      setOtpSessionId(data.otp_session_id);
      setEmailHint(data.email_hint);
      setExpiresIn(data.expires_in_seconds);
      setCooldown(60);
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not resend OTP");
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-paper-raised border border-ink-900/[0.08] rounded-2xl shadow-card p-8">
        <h1 className="font-display text-3xl text-ink-900 mb-2">Verify it's you</h1>
        <p className="font-body text-sm text-ink-600 mb-8">
          We sent a 6-digit code to{" "}
          <span className="text-fiber-teal font-mono">{emailHint}</span>
        </p>

        <form onSubmit={handleSubmit}>
          <div className="flex justify-between gap-2 mb-6" onPaste={handlePaste}>
            {digits.map((d, i) => (
              <input
                key={i}
                ref={(el) => (inputRefs.current[i] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={d}
                onChange={(e) => handleDigitChange(i, e.target.value)}
                onKeyDown={(e) => handleKeyDown(i, e)}
                className="w-12 h-14 text-center text-xl font-mono bg-paper border border-ink-900/[0.12]
                           rounded-lg text-ink-900 focus:outline-none focus:border-fiber-teal
                           focus:ring-1 focus:ring-fiber-teal transition-colors"
              />
            ))}
          </div>

          {error && (
            <p className="font-body text-sm text-fiber-rust mb-4">{error}</p>
          )}

          <p className="font-mono text-xs text-ink-400 mb-6">
            {expiresIn > 0 ? `Code expires in ${formatTime(expiresIn)}` : "Code expired — please resend"}
          </p>

          <button
            type="submit"
            disabled={loading || expiresIn <= 0}
            className="w-full py-3 rounded-lg bg-fiber-teal text-white font-body font-semibold
                       hover:bg-fiber-teal/90 disabled:opacity-40 disabled:cursor-not-allowed
                       transition-colors"
          >
            {loading ? "Verifying..." : "Verify & Continue"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={handleResend}
            disabled={cooldown > 0 || resendLoading}
            className="font-body text-sm text-fiber-amber hover:text-fiber-amber/80
                       disabled:text-ink-400 disabled:cursor-not-allowed transition-colors"
          >
            {resendLoading
              ? "Resending..."
              : cooldown > 0
              ? `Resend code in ${cooldown}s`
              : "Resend code"}
          </button>
        </div>
      </div>
    </div>
  );
}