import { useState, useEffect, useCallback } from "react";
import { Users, Database, ScanSearch, Lightbulb, Activity, ShieldCheck } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import GlassCard from "../components/GlassCard";
import StatCard from "../components/StatCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import SustainabilityPieChart from "../charts/SustainabilityPieChart";
import { getAdminDashboard } from "../services/api";

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getAdminDashboard()
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Could not load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const roleData = data ? Object.entries(data.users_by_role).map(([name, value]) => ({ name, value })) : [];

  return (
    <div className="px-8 py-8 max-w-7xl mx-auto">
      <Breadcrumbs />

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl text-ink-900 tracking-tight">Admin Dashboard</h1>
          <p className="font-body text-sm text-ink-500 mt-1.5">Platform-wide usage, users, and system status.</p>
        </div>
        {data && (
          <span className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-mono font-semibold border ${
            data.system_status === "healthy"
              ? "bg-fiber-moss/10 text-fiber-moss border-fiber-moss/20"
              : "bg-fiber-rust/10 text-fiber-rust border-fiber-rust/20"
          }`}>
            <ShieldCheck className="w-3.5 h-3.5" />
            {data.system_status.toUpperCase()}
          </span>
        )}
      </div>

      {loading && <LoadingState label="Loading platform analytics..." />}
      {!loading && error && <ErrorState message={error} onRetry={fetchData} />}

      {!loading && !error && data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total Users" value={data.total_users} icon={<Users className="w-4 h-4" />} accent="teal" />
            <StatCard label="Waste Records" value={data.total_waste_records} icon={<Database className="w-4 h-4" />} accent="moss" />
            <StatCard label="Analyses Run" value={data.total_analyses} icon={<ScanSearch className="w-4 h-4" />} accent="amber" />
            <StatCard label="Recommendations" value={data.total_recommendations} icon={<Lightbulb className="w-4 h-4" />} accent="rust" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <GlassCard accent="teal">
              <h2 className="font-display text-lg text-ink-900 mb-4">Users by Role</h2>
              {roleData.length > 0
                ? <SustainabilityPieChart data={roleData} height={220} />
                : <EmptyState message="No users yet." />}
            </GlassCard>

            <GlassCard accent="amber" className="lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-4 h-4 text-fiber-amber" />
                <h2 className="font-display text-lg text-ink-900">Recent Activity</h2>
              </div>
              {data.recent_activity.length === 0 ? (
                <EmptyState message="No recent activity." />
              ) : (
                <div className="space-y-2">
                  {data.recent_activity.map((a, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-ink-900/[0.02] border border-ink-900/[0.05]">
                      <span className="text-sm text-ink-700 font-body">{a.description}</span>
                      <span className="text-xs text-ink-400 font-mono">{new Date(a.timestamp).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              )}
            </GlassCard>

            <GlassCard accent="moss">
              <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-1 font-body">Total Reports Generated</p>
              <p className="text-3xl font-mono font-semibold text-fiber-moss">{data.total_reports}</p>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}