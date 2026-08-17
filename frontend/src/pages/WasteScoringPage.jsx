import React, { useState } from "react";
import { Link } from "react-router-dom";
import AnalyzeForm from "../components/AnalyzeForm";
import GlassCard from "../components/GlassCard";
import ProgressBar from "../components/ProgressBar";
import { EmptyState } from "../components/StatusStates";
import { ArrowLeft, Gauge } from "lucide-react";

export default function WasteScoringPage() {
  const [result, setResult] = useState(null);
  const scores = result?.scores;

  return (
    <div className="min-h-screen bg-paper p-6 md:p-10">
      <Link to="/sustainability" className="inline-flex items-center gap-1.5 text-xs text-ink-500 hover:text-ink-900 mb-6 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Sustainability Dashboard
      </Link>

      <div className="mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-fiber-amber/10 border border-fiber-amber/25 flex items-center justify-center">
          <Gauge className="w-5 h-5 text-fiber-amber" />
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-amber font-mono mb-1">Waste Scoring</p>
          <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink-900">Score Breakdown</h1>
        </div>
      </div>

      <AnalyzeForm onResult={setResult} />

      {!result ? (
        <EmptyState message="Run an analysis above to see waste scores." />
      ) : (
        <GlassCard accent="amber">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-display text-lg text-fiber-sand">Score Breakdown</h2>
            <span className="px-3 py-1 rounded-full bg-fiber-amber/10 border border-fiber-amber/25 text-fiber-amber text-sm font-semibold">
              {scores.category}
            </span>
          </div>

          {/* Note: ProgressBar only supports teal/amber/moss/rust accents — the
              previous emerald/blue/violet/rose values silently fell back to teal
              for every bar, which is why they all looked identical. */}
          <ProgressBar label="Recyclability" value={scores.recyclability} color="teal" />
          <ProgressBar label="Reuse" value={scores.reuse} color="moss" />
          <ProgressBar label="Sustainability" value={scores.sustainability} color="amber" />
          <ProgressBar label="Material Recovery" value={scores.recovery} color="rust" />
          <ProgressBar label="Circularity" value={scores.circularity} color="teal" />
        </GlassCard>
      )}
    </div>
  );
}
