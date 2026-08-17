import { useState, useEffect, useCallback } from "react";
import { Boxes, Recycle, Repeat, Gauge, TrendingUp } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import GlassCard from "../components/GlassCard";
import StatCard from "../components/StatCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import SustainabilityBarChart from "../charts/SustainabilityBarChart";
import SustainabilityLineChart from "../charts/SustainabilityLineChart";
import { getRecyclerDashboard } from "../services/api";

export default function RecyclerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getRecyclerDashboard({ start_date: startDate || undefined, end_date: endDate || undefined })
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Could not load dashboard."))
      .finally(() => setLoading(false));
  }, [startDate, endDate]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const materialChartData = data
    ? Object.entries(data.waste_by_material).map(([label, value]) => ({ label, value }))
    : [];

  const categoryChartData = data
    ? Object.entries(data.waste_by_category).map(([label, value]) => ({ label, value }))
    : [];

  const trendData = data?.processing_trend?.map((t) => ({ label: t.date.slice(5), processed: t.processed_kg })) || [];

  return (
    <div className="px-8 py-8 max-w-7xl mx-auto">
      <Breadcrumbs />

      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-3xl text-ink-900 tracking-tight">Recycling Facility Dashboard</h1>
          <p className="font-body text-sm text-ink-500 mt-1.5">Inventory, processing, and recovery analytics.</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
            className="rounded-lg bg-paper-raised border border-ink-900/10 text-ink-900 px-3 py-2 text-sm focus:outline-none focus:border-fiber-teal/60"
          />
          <span className="text-ink-400 text-sm">to</span>
          <input
            type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
            className="rounded-lg bg-paper-raised border border-ink-900/10 text-ink-900 px-3 py-2 text-sm focus:outline-none focus:border-fiber-teal/60"
          />
        </div>
      </div>

      {loading && <LoadingState label="Loading facility analytics..." />}
      {!loading && error && <ErrorState message={error} onRetry={fetchData} />}

      {!loading && !error && data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total Received" value={data.total_waste_received_kg.toLocaleString()} unit="kg" icon={<Boxes className="w-4 h-4" />} accent="teal" />
            <StatCard label="Pending" value={data.pending_waste_kg.toLocaleString()} unit="kg" icon={<Gauge className="w-4 h-4" />} accent="amber" />
            <StatCard label="Processed" value={data.processed_waste_kg.toLocaleString()} unit="kg" icon={<Recycle className="w-4 h-4" />} accent="moss" />
            <StatCard label="Avg Diversion" value={data.waste_diversion_avg_pct} unit="%" icon={<TrendingUp className="w-4 h-4" />} accent="rust" />
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard label="Recycling Opportunities" value={data.recycling_opportunities} accent="teal" />
            <StatCard label="Reuse Opportunities" value={data.reuse_opportunities} icon={<Repeat className="w-4 h-4" />} accent="moss" />
            <StatCard label="Avg Material Recovery" value={data.material_recovery_avg_pct} unit="%" accent="amber" />
            <StatCard label="Waste Categories" value={Object.keys(data.waste_by_category).length} accent="rust" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard accent="teal">
              <h2 className="font-display text-lg text-ink-900 mb-4">Waste by Material</h2>
              {materialChartData.length > 0
                ? <SustainabilityBarChart data={materialChartData} color="#1F6F5C" height={240} />
                : <EmptyState message="No material data for this range." />}
            </GlassCard>

            <GlassCard accent="amber">
              <h2 className="font-display text-lg text-ink-900 mb-4">Waste by Category</h2>
              {categoryChartData.length > 0
                ? <SustainabilityBarChart data={categoryChartData} color="#B9791F" height={240} />
                : <EmptyState message="No category data yet." />}
            </GlassCard>

            <GlassCard accent="moss" className="lg:col-span-2">
              <h2 className="font-display text-lg text-ink-900 mb-4">Processing Trend (last 14 days)</h2>
              {trendData.length > 0
                ? <SustainabilityLineChart data={trendData} lines={[{ key: "processed", color: "#4C7A46", name: "Processed (kg)" }]} height={260} />
                : <EmptyState message="No processing activity recorded yet." />}
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}