import { useState, useEffect, useCallback } from "react";
import { Factory, Recycle, Repeat, Leaf } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import GlassCard from "../components/GlassCard";
import StatCard from "../components/StatCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import SustainabilityAreaChart from "../charts/SustainabilityAreaChart";
import SustainabilityBarChart from "../charts/SustainabilityBarChart";
import { getManufacturerDashboard } from "../services/api";

export default function ManufacturerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getManufacturerDashboard({})
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Could not load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const genTrend = data?.waste_generation_trend?.map((t) => ({ label: t.date.slice(5), value: t.kg })) || [];
  const materialData = data ? Object.entries(data.waste_by_material).map(([label, value]) => ({ label, value })) : [];

  return (
    <div className="px-8 py-8 max-w-7xl mx-auto">
      <Breadcrumbs />

      <div className="mb-8">
        <h1 className="font-display text-3xl text-ink-900 tracking-tight">Manufacturer Dashboard</h1>
        <p className="font-body text-sm text-ink-500 mt-1.5">Your production waste, recovery, and sustainability performance.</p>
      </div>

      {loading && <LoadingState label="Loading production analytics..." />}
      {!loading && error && <ErrorState message={error} onRetry={fetchData} />}

      {!loading && !error && data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total Production Waste" value={data.total_production_waste_kg.toLocaleString()} unit="kg" icon={<Factory className="w-4 h-4" />} accent="teal" />
            <StatCard label="Recycling Opportunities" value={data.recycling_opportunities} icon={<Recycle className="w-4 h-4" />} accent="moss" />
            <StatCard label="Reuse Opportunities" value={data.reuse_opportunities} icon={<Repeat className="w-4 h-4" />} accent="amber" />
            <StatCard label="Sustainability Score" value={data.sustainability_performance_score} unit="/100" icon={<Leaf className="w-4 h-4" />} accent="rust" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard accent="teal" className="lg:col-span-2">
              <h2 className="font-display text-lg text-ink-900 mb-4">Waste Generation Trend</h2>
              {genTrend.length > 0
                ? <SustainabilityAreaChart data={genTrend} color="#1F6F5C" height={260} />
                : <EmptyState message="No batches logged yet." />}
            </GlassCard>

            <GlassCard accent="amber">
              <h2 className="font-display text-lg text-ink-900 mb-4">Waste by Material</h2>
              {materialData.length > 0
                ? <SustainabilityBarChart data={materialData} color="#B9791F" height={240} />
                : <EmptyState message="No material data yet." />}
            </GlassCard>

            <GlassCard accent="moss">
              <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-1 font-body">Material Recovery Potential</p>
              <p className="text-3xl font-mono font-semibold text-fiber-moss">
                {data.material_recovery_potential_kg.toLocaleString()}
                <span className="text-lg text-ink-400 ml-2">kg</span>
              </p>
              <p className="text-sm text-ink-500 mt-3 font-body">
                Estimated recoverable material from your logged waste batches, based on recyclability analysis.
              </p>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}