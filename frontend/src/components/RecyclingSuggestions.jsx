import React from "react";
import SustainabilityMeter from "../charts/SustainabilityMeter.jsx";
import { Leaf, ArrowRight, Lightbulb } from "lucide-react";

export default function RecyclingSuggestions({ recommendation, recyclability }) {
  if (!recommendation) return null;

  const {
    best_recycling_method, ranked_methods, sustainability_score,
    environmental_impact_score, reuse_suggestions, waste_reduction_strategies,
  } = recommendation;

  return (
    <div className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Leaf className="w-4 h-4 text-fiber-moss" />
        <h3 className="font-display text-lg text-ink-900">Recycling Recommendation</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 flex flex-col items-center justify-center gap-4">
          <SustainabilityMeter score={sustainability_score} label="Sustainability" color="#4C7A46" />
          <SustainabilityMeter score={environmental_impact_score} label="Environmental Impact" color="#1F6F5C" />
        </div>

        <div className="md:col-span-2">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs uppercase tracking-wider text-ink-500">Best Method</span>
            <span className="text-fiber-amber font-display text-lg">{best_recycling_method}</span>
          </div>

          <div className="space-y-1.5 mb-4">
            {(ranked_methods || []).slice(0, 4).map((m) => (
              <div key={m.method} className="flex items-center gap-2">
                <span className="w-32 text-xs text-ink-600 truncate">{m.method}</span>
                <div className="flex-1 h-1.5 bg-ink-900/[0.06] rounded-full overflow-hidden">
                  <div className="h-full bg-fiber-teal" style={{ width: `${Math.min(100, m.score)}%` }} />
                </div>
                <span className="w-10 text-right text-[11px] font-mono text-ink-500">{Math.round(m.score)}</span>
              </div>
            ))}
          </div>

          {recyclability && (
            <p className="text-xs text-ink-600 leading-relaxed mb-4">
              {recyclability.disposal_recommendation}
            </p>
          )}

          {reuse_suggestions?.length > 0 && (
            <div className="mb-3">
              <p className="text-xs uppercase tracking-wider text-ink-500 mb-1.5 flex items-center gap-1.5">
                <ArrowRight className="w-3 h-3" /> Reuse Suggestions
              </p>
              <ul className="space-y-1">
                {reuse_suggestions.map((s, i) => (
                  <li key={i} className="text-sm text-ink-700 flex gap-2">
                    <span className="text-fiber-moss">•</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {waste_reduction_strategies?.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wider text-ink-500 mb-1.5 flex items-center gap-1.5">
                <Lightbulb className="w-3 h-3" /> Waste Reduction Strategies
              </p>
              <ul className="space-y-1">
                {waste_reduction_strategies.map((s, i) => (
                  <li key={i} className="text-sm text-ink-700 flex gap-2">
                    <span className="text-fiber-amber">•</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}