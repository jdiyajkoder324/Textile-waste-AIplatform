import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboardSummary } from "../services/sustainabilityApi";
import StatCard from "../components/StatCard";
import GlassCard from "../components/GlassCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import SustainabilityPieChart from "../charts/SustainabilityPieChart";
import { Droplets, Recycle, Gauge, Lightbulb, FileText, ArrowRight, Globe2, Boxes } from "lucide-react";

const SUB_PAGES = [
  { to: "/sustainability/environmental-impact", label: "Environmental Impact", desc: "CO2, water & landfill savings", icon: Droplets, accent: "teal" },
  { to: "/sustainability/circular-economy", label: "Circular Economy", desc: "Circularity & recovery scores", icon: Recycle, accent: "moss" },
  { to: "/sustainability/waste-scoring", label: "Waste Scoring", desc: "0–100 breakdown per batch", icon: Gauge, accent: "amber" },
  { to: "/sustainability/recommendations", label: "Recommendations", desc: "Actionable next steps", icon: Lightbulb, accent: "rust" },
  { to: "/sustainability/report", label: "Full Report", desc: "Downloadable JSON summary", icon: FileText, accent: "teal" },
];

const ACCENT_CLASSES = {
  teal: "text-fiber-teal bg-fiber-teal/10 border-fiber-teal/20 group-hover:border-fiber-teal/40 group-hover:shadow-[0_0_30px_-14px_rgba(31,111,92,0.35)]",
  moss: "text-fiber-moss bg-fiber-moss/10 border-fiber-moss/20 group-hover:border-fiber-moss/40 group-hover:shadow-[0_0_30px_-14px_rgba(76,122,70,0.3)]",
  amber: "text-fiber-amber bg-fiber-amber/10 border-fiber-amber/20 group-hover:border-fiber-amber/40 group-hover:shadow-[0_0_30px_-14px_rgba(185,121,31,0.3)]",
  rust: "text-fiber-rust bg-fiber-rust/10 border-fiber-rust/20 group-hover:border-fiber-rust/40 group-hover:shadow-[0_0_30px_-14px_rgba(178,59,46,0.3)]",
};

export default function SustainabilityDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not load dashboard summary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return (
    <div className="min-h-screen bg-paper">
      <div className="p-6 md:p-10 max-w-7xl mx-auto">
        <div className="mb-8 flex items-end justify-between flex-wrap gap-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-teal font-mono mb-2 flex items-center gap-2">
              <Globe2 className="w-3.5 h-3.5" /> Sustainability Intelligence
            </p>
            <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink-900 tracking-tight">
              Circularity Dashboard
            </h1>
            <p className="text-ink-600 text-sm mt-2 max-w-lg font-body">
              Woven from every batch you've analyzed — carbon, water, and material
              recovered back into the loop.
            </p>
          </div>
          {summary && (
            <p className="text-xs font-mono text-ink-400">
              Updated {new Date(summary.last_updated).toLocaleTimeString()}
            </p>
          )}
        </div>

        <div className="mb-10">
          <p className="text-xs uppercase tracking-wider text-ink-400 mb-3 font-body">Explore</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {SUB_PAGES.map(({ to, label, desc, icon: Icon, accent }) => (
              <Link
                key={to}
                to={to}
                className="group relative rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-4 transition-all duration-300 hover:-translate-y-0.5"
              >
                <div className={`w-9 h-9 rounded-lg border flex items-center justify-center mb-3 transition-all ${ACCENT_CLASSES[accent]}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <p className="text-sm font-semibold text-ink-900">{label}</p>
                <p className="text-xs text-ink-400 mt-0.5 leading-snug">{desc}</p>
                <ArrowRight className="w-3.5 h-3.5 text-ink-300 absolute top-4 right-4 group-hover:text-ink-600 group-hover:translate-x-0.5 transition-all" />
              </Link>
            ))}
          </div>
        </div>

        {loading && <LoadingState label="Spinning up the numbers..." />}
        {!loading && error && <ErrorState message={error} onRetry={fetchSummary} />}

        {!loading && !error && (!summary || summary.total_batches === 0) && (
          <EmptyState message="No waste batches analyzed yet. Run a sustainability analysis to see your dashboard come alive." />
        )}

        {!loading && !error && summary && summary.total_batches > 0 && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
              <StatCard label="CO2 Saved" value={summary.total_co2_saved.toLocaleString()} unit="kg" icon="🌍" accent="teal" />
              <StatCard label="Water Saved" value={summary.total_water_saved.toLocaleString()} unit="L" icon="💧" accent="moss" />
              <StatCard label="Circularity" value={summary.average_circularity_score.toFixed(1)} unit="/100" icon="♻️" accent="amber" />
              <StatCard label="Waste Diverted" value={summary.average_waste_diverted_percentage.toFixed(1)} unit="%" icon={<Boxes className="w-4 h-4" />} accent="rust" />
              <StatCard label="Batches" value={summary.total_batches} unit="" icon="🧵" accent="teal" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <GlassCard className="lg:col-span-2" accent="teal">
                <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-3 font-body">Total Waste Analyzed</p>
                <p className="text-5xl font-mono font-semibold text-fiber-teal">
                  {summary.total_waste_analyzed_kg.toLocaleString()}
                  <span className="text-lg text-ink-400 ml-2">kg</span>
                </p>
                <div className="h-px w-full my-6 bg-ink-900/[0.08]" />
                <p className="text-sm text-ink-400 font-body">
                  Across {summary.total_batches} batch{summary.total_batches !== 1 ? "es" : ""} logged so far.
                </p>
              </GlassCard>

              <GlassCard accent="amber">
                <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-3 font-body">Rating Distribution</p>
                {Object.keys(summary.rating_distribution || {}).length > 0 ? (
                  <SustainabilityPieChart
                    data={Object.entries(summary.rating_distribution).map(([name, value]) => ({ name, value }))}
                    height={220}
                  />
                ) : (
                  <EmptyState message="No rating data yet." />
                )}
              </GlassCard>
            </div>
          </>
        )}
      </div>
    </div>
  );
}