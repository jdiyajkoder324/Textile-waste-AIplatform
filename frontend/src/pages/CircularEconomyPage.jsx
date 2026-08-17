import React, { useState } from "react";
import { Link } from "react-router-dom";
import AnalyzeForm from "../components/AnalyzeForm";
import GlassCard from "../components/GlassCard";
import { EmptyState } from "../components/StatusStates";
import GaugeChart from "../charts/GaugeChart";
import { ArrowLeft, Recycle } from "lucide-react";

export default function CircularEconomyPage() {
  const [result, setResult] = useState(null);

  const ce = result?.circular_economy;
  const scores = result?.scores;

  return (
    <div className="min-h-screen bg-paper p-6 md:p-10">
      <Link to="/sustainability" className="inline-flex items-center gap-1.5 text-xs text-ink-500 hover:text-ink-900 mb-6 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Sustainability Dashboard
      </Link>

      <div className="mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-fiber-moss/10 border border-fiber-moss/20 flex items-center justify-center">
          <Recycle className="w-5 h-5 text-fiber-moss" />
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-moss font-mono mb-1">Circular Economy</p>
          <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink-900">Circular Economy Analytics</h1>
        </div>
      </div>

      <AnalyzeForm onResult={setResult} />

      {!result ? (
        <EmptyState message="Run an analysis above to see circular economy analytics." />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <GlassCard accent="amber">
              <GaugeChart value={ce.score} label="Circular Economy Score" accent="amber" />
            </GlassCard>
            <GlassCard accent="teal">
              <GaugeChart value={scores.recovery} label="Recovery Score" accent="teal" />
            </GlassCard>
            <GlassCard accent="moss">
              <GaugeChart value={scores.sustainability} label="Sustainability Score" accent="moss" />
            </GlassCard>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard accent="teal">
              <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-1 font-body">Utilization</p>
              <p className="text-3xl font-mono font-semibold text-ink-900">{ce.utilization}%</p>
            </GlassCard>
            <GlassCard accent="amber">
              <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-1 font-body">Optimization</p>
              <p className="text-3xl font-mono font-semibold text-ink-900">{ce.optimization}%</p>
            </GlassCard>
            <GlassCard accent="moss">
              <p className="text-[11px] uppercase tracking-[0.14em] text-ink-400 mb-1 font-body">Category</p>
              <p className="text-xl font-display font-semibold text-fiber-amber">{ce.category}</p>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}