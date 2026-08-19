import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard, ScanLine, Package, History,
  Leaf, Sparkles, FileText, User, LogOut, BarChart3, Users,
} from "lucide-react";
import NotificationBell from "../components/NotificationBell";

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const roleAnalyticsItem =
  user?.role === "Recycler" ? { to: "/analytics/recycler", label: "Facility Analytics", icon: BarChart3 } :
  user?.role === "Industry" ? { to: "/analytics/manufacturer", label: "Manufacturer Dashboard", icon: BarChart3 } :
  user?.role === "Admin" ? { to: "/analytics/admin", label: "Admin Dashboard", icon: BarChart3 } :
  null;

  const NAV_ITEMS = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/upload", label: "Analyze Textile", icon: ScanLine },
  { to: "/inventory", label: "Inventory", icon: Package },
  { to: "/history", label: "Analysis History", icon: History },
  { to: "/sustainability", label: "Sustainability", icon: Leaf },
  { to: "/sustainability/recommendations", label: "Recommendations", icon: Sparkles },
  { to: "/reports", label: "Reports", icon: FileText },
  ...(roleAnalyticsItem ? [roleAnalyticsItem] : []),
  ...(user?.role === "Admin" ? [{ to: "/admin/users", label: "User Management", icon: Users }] : []),
  { to: "/profile", label: "Profile", icon: User },
];
  return (
    <div className="min-h-screen bg-paper flex">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 h-screen sticky top-0 border-r border-ink-900/[0.06] bg-paper-raised flex flex-col">
        <div className="px-6 py-6 border-b border-ink-900/[0.06] flex items-center justify-between">
          <div>
            <h1 className="font-display text-xl text-ink-900 tracking-tight">
              Textile<span className="text-fiber-teal">Intel</span>
            </h1>
            <p className="font-mono text-[11px] text-ink-400 mt-1 uppercase tracking-wider">
              {user?.role || "Member"}
            </p>
          </div>
          <NotificationBell />
        </div>

        <nav className="flex-1 px-3 py-4 flex flex-col gap-1 overflow-y-auto">
          {NAV_ITEMS.map(({ to, label, icon: Icon }, i) => (
            <NavLink
              key={`${to}-${i}`}
              to={to}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 px-3 py-2.5 rounded-lg font-body text-sm transition-all duration-200 ${
                  isActive
                    ? "bg-fiber-teal/[0.08] text-fiber-teal"
                    : "text-ink-600 hover:text-ink-900 hover:bg-ink-900/[0.03]"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-full bg-fiber-teal" />
                  )}
                  <Icon size={17} strokeWidth={isActive ? 2.2 : 1.8} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-ink-900/[0.06]">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-body text-sm
                       text-fiber-rust/80 hover:text-fiber-rust hover:bg-fiber-rust/[0.06] transition-colors"
          >
            <LogOut size={17} strokeWidth={1.8} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 h-screen overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}