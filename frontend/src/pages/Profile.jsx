import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  User as UserIcon, Mail, ShieldCheck, LogOut, KeyRound, Copy, Check,
} from "lucide-react";

const ROLE_STYLES = {
  Industry: "text-fiber-teal border-fiber-teal/30 bg-fiber-teal/10",
  Recycler: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10",
  Admin: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10",
};

export default function Profile() {
  const { user, logout } = useAuth();
  const [copied, setCopied] = useState(false);

  const handleCopyEmail = () => {
    if (!user?.email) return;
    navigator.clipboard.writeText(user.email);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const roleStyle = ROLE_STYLES[user?.role] || ROLE_STYLES.Industry;
  const initials = (user?.name || "?")
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div>
      <header className="mb-8">
        <h1 className="font-display text-3xl text-ink-900 tracking-tight">Profile</h1>
        <p className="text-sm text-ink-500 mt-1.5">Manage your account details and session.</p>
      </header>

      {!user ? (
        <div className="card-panel p-6 text-sm text-ink-500">Loading profile...</div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_2fr] gap-8 items-start">
          {/* Identity card */}
          <section className="card-panel p-6 flex flex-col items-center text-center">
            <div className="w-20 h-20 rounded-2xl bg-fiber-teal/10 border border-fiber-teal/20 flex items-center justify-center">
              <span className="font-display text-2xl text-fiber-teal">{initials}</span>
            </div>
            <h2 className="font-display text-xl text-ink-900 mt-4">{user.name}</h2>
            <p className="text-sm text-ink-500 mt-0.5">{user.email}</p>
            <span
              className={`inline-flex items-center gap-1.5 mt-4 px-3 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-wide ${roleStyle}`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              {user.role}
            </span>

            <div className="thread-divider w-full my-6" />

            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-lg border border-ink-900/[0.08] text-ink-500 text-sm font-medium hover:bg-fiber-rust/10 hover:text-fiber-rust hover:border-fiber-rust/25 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Log out
            </button>
          </section>

          {/* Account details */}
          <div className="flex flex-col gap-8">
            <section className="card-panel p-6">
              <div className="flex items-center gap-2 mb-5">
                <UserIcon className="w-4 h-4 text-fiber-teal" />
                <h2 className="font-display text-lg text-ink-900">Account Details</h2>
              </div>

              <div className="divide-y divide-ink-900/[0.06]">
                <div className="flex items-center justify-between gap-4 py-3.5">
                  <div className="flex items-center gap-2.5 text-ink-500 text-sm">
                    <UserIcon className="w-4 h-4" />
                    Full name
                  </div>
                  <span className="text-sm font-medium text-ink-900">{user.name}</span>
                </div>

                <div className="flex items-center justify-between gap-4 py-3.5">
                  <div className="flex items-center gap-2.5 text-ink-500 text-sm">
                    <Mail className="w-4 h-4" />
                    Email address
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-ink-900">{user.email}</span>
                    <button
                      onClick={handleCopyEmail}
                      title="Copy email"
                      className="w-7 h-7 rounded-lg border border-ink-900/10 flex items-center justify-center text-ink-400 hover:text-fiber-teal hover:border-fiber-teal/25 hover:bg-fiber-teal/10 transition-colors"
                    >
                      {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-4 py-3.5">
                  <div className="flex items-center gap-2.5 text-ink-500 text-sm">
                    <ShieldCheck className="w-4 h-4" />
                    Role
                  </div>
                  <span
                    className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-wide ${roleStyle}`}
                  >
                    {user.role}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-4 py-3.5">
                  <div className="flex items-center gap-2.5 text-ink-500 text-sm">
                    <KeyRound className="w-4 h-4" />
                    User ID
                  </div>
                  <span className="font-mono text-sm text-ink-600">#{user.id}</span>
                </div>
              </div>
            </section>

            <section className="card-panel p-6">
              <div className="flex items-center gap-2 mb-3">
                <ShieldCheck className="w-4 h-4 text-fiber-amber" />
                <h2 className="font-display text-lg text-ink-900">Security</h2>
              </div>
              <p className="text-sm text-ink-500">
                Login is protected with OTP-based two-factor verification sent to your registered email.
                Password changes and profile editing aren't available yet — reach out to an Admin if your
                details need updating.
              </p>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}