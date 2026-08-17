import React, { useState } from "react";
import { Link } from "react-router-dom";
import AnalyzeForm from "../components/AnalyzeForm";
import GlassCard from "../components/GlassCard";
import { EmptyState } from "../components/StatusStates";
import SustainabilityBarChart from "../charts/SustainabilityBarChart";
import SustainabilityAreaChart from "../charts/SustainabilityAreaChart";
import SustainabilityPieChart from "../charts/SustainabilityPieChart";
import { ArrowLeft, Droplets, CloudDrizzle, Waves, Trash2, Zap } from "lucide-react";

export default function EnvironmentalImpactPage() {
  const [result, setResult] = useState(null);

  const env = result?.environmental_report;

  const resourceChartData = env
    ? [
        { label: "CO2 Saved (kg)", value: env.co2_saved },
        { label: "Water Saved (L)", value: env.water_saved / 100 },
        { label: "Landfill Saved (kg)", value: env.landfill_saved },
        { label: "Energy Saved (kWh)", value: env.energy_saved },
      ]
    : [];

  const landfillPieData = env
    ? [
        { name: "Diverted from Landfill", value: env.landfill_saved },
        { name: "Remaining Impact", value: Math.max(result.weight_kg - env.landfill_saved, 0.01) },
      ]
    : [];

  const statTiles = env
    ? [
        { label: "CO2 Saved", value: `${env.co2_saved} kg`, icon: CloudDrizzle, accent: "teal" },
        { label: "Water Saved", value: `${env.water_saved.toLocaleString()} L`, icon: Waves, accent: "moss" },
        { label: "Landfill Reduced", value: `${env.landfill_saved} kg`, icon: Trash2, accent: "amber" },
        { label: "Energy Saved", value: `${env.energy_saved} kWh`, icon: Zap, accent: "rust" },
      ]
    : [];

  const accentText = {
    teal: "text-fiber-teal bg-fiber-teal/10 border-fiber-teal/20",
    moss: "text-fiber-moss bg-fiber-moss/10 border-fiber-moss/20",
    amber: "text-fiber-amber bg-fiber-amber/10 border-fiber-amber/20",
    rust: "text-fiber-rust bg-fiber-rust/10 border-fiber-rust/20",
  };

  return (
    <div className="min-h-screen bg-paper p-6 md:p-10">
      <Link to="/sustainability" className="inline-flex items-center gap-1.5 text-xs text-ink-500 hover:text-ink-900 mb-6 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Sustainability Dashboard
      </Link>

      <div className="mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-fiber-teal/10 border border-fiber-teal/20 flex items-center justify-center">
          <Droplets className="w-5 h-5 text-fiber-teal" />
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-teal font-mono mb-1">Environmental Impact</p>
          <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink-900">CO2, Water & Resource Recovery</h1>
        </div>
      </div>

      <AnalyzeForm onResult={setResult} />

      {!result ? (
        <EmptyState message="Run an analysis above to see environmental impact charts." />
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {statTiles.map(({ label, value, icon: Icon, accent }) => (
              <div key={label} className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-5">
                <div className={`w-9 h-9 rounded-lg border flex items-center justify-center mb-3 ${accentText[accent]}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <p className="text-xs uppercase tracking-wider text-ink-500">{label}</p>
                <p className="text-xl font-mono font-semibold text-ink-900 mt-1">{value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard accent="teal">
              <h2 className="font-display text-lg text-ink-900 mb-4">CO2 & Water Chart</h2>
              <SustainabilityBarChart data={resourceChartData} color="#1F6F5C" />
            </GlassCard>

            <GlassCard accent="moss">
              <h2 className="font-display text-lg text-ink-900 mb-4">Resource Recovery Trend</h2>
              <SustainabilityAreaChart data={resourceChartData} color="#4C7A46" />
            </GlassCard>

            <GlassCard accent="amber">
              <h2 className="font-display text-lg text-ink-900 mb-4">Landfill Reduction</h2>
              <SustainabilityPieChart data={landfillPieData} height={240} />
            </GlassCard>

            <GlassCard accent="rust">
              <h2 className="font-display text-lg text-ink-900 mb-2">Rating & Recommendation</h2>
              <p className="text-3xl font-display font-semibold text-fiber-teal mb-2">{env.rating}</p>
              <p className="text-sm text-ink-600 font-body">{env.recommendation}</p>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}