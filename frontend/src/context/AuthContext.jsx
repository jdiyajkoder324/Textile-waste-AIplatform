import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";
import { loginStep1, verifyOtp as verifyOtpApi, resendOtp as resendOtpApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      const savedToken = localStorage.getItem("token");
      if (!savedToken) {
        setLoading(false);
        return;
      }
      try {
        const me = await api.get("/user/me");
        setUser(me.data);
        setToken(savedToken);
      } catch (err) {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, []);

  // Step 1 — email + password, triggers OTP send
  const initiateLogin = async (email, password) => {
    const res = await loginStep1(email, password);
    // res.data = { message, otp_session_id, email_hint, expires_in_seconds }
    return res.data;
  };

  // Step 2 — call after user enters OTP
  const completeLogin = async (otp_session_id, otp) => {
    const res = await verifyOtpApi(otp_session_id, otp);
    const { access_token } = res.data;

    localStorage.setItem("token", access_token);
    setToken(access_token);

    // fetch the real user object from backend instead of decoding the JWT
    const me = await api.get("/user/me");
    setUser(me.data);

    return me.data;
  };

  const resendLoginOtp = async (otp_session_id) => {
    const res = await resendOtpApi(otp_session_id);
    return res.data;
  };

  const register = async (name, email, password, role) => {
    const res = await api.post("/user/register", { name, email, password, role });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role: user?.role || null,
        isAuthenticated: !!token,
        loading,
        register,
        logout,
        initiateLogin,
        completeLogin,
        resendLoginOtp,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}