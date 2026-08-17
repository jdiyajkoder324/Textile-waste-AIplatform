import React, { useState } from "react";
import { Link } from "react-router-dom";
import AnalyzeForm from "../components/AnalyzeForm";
import GlassCard from "../components/GlassCard";
import { EmptyState } from "../components/StatusStates";
import { ArrowLeft, Lightbulb, Recycle, Repeat, Leaf, Trash2 } from "lucide-react";

const CARD_META = [
  { key: "recycling", title: "Recycling Recommendation", icon: Recycle, accent: "teal" },
  { key: "reuse", title: "Reuse Recommendation", icon: Repeat, accent: "moss" },
  { key: "sustainability", title: "Sustainability Suggestion", icon: Leaf, accent: "amber" },
  { key: "disposal", title: "Disposal Suggestion", icon: Trash2, accent: "rust" },
];

const ACCENT_TEXT = {
  teal: "text-fiber-teal",
  moss: "text-fiber-moss",
  amber: "text-fiber-amber",
  rust: "text-fiber-rust",
};

function bucketRecommendations(recommendations = []) {
  const buckets = { recycling: [], reuse: [], sustainability: [], disposal: [] };
  recommendations.forEach((rec) => {
    const lower = rec.toLowerCase();
    if (lower.includes("dispos")) buckets.disposal.push(rec);
    else if (lower.includes("recycl") || lower.includes("separation")) buckets.recycling.push(rec);
    else if (lower.includes("reuse") || lower.includes("donat") || lower.includes("upcycl")) buckets.reuse.push(rec);
    else buckets.sustainability.push(rec);
  });
  return buckets;
}

export default function RecommendationPage() {
  const [result, setResult] = useState(null);

  const buckets = result ? bucketRecommendations(result.recommendations) : null;

  return (
    <div className="min-h-screen bg-paper p-6 md:p-10">
      <Link to="/sustainability" className="inline-flex items-center gap-1.5 text-xs text-ink-500 hover:text-ink-900 mb-6 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Sustainability Dashboard
      </Link>

      <div className="mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-fiber-rust/10 border border-fiber-rust/25 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-fiber-rust" />
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-rust font-mono mb-1">Recommendations</p>
          <h1 className="text-2xl md:text-3xl font-display font-display font-semibold text-ink-900">Actionable Next Steps</h1>
        </div>
      </div>

      <AnalyzeForm onResult={setResult} />

      {!result ? (
        <EmptyState message="Run an analysis above to see recommendations." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {CARD_META.map(({ key, title, icon: Icon, accent }) => (
            <GlassCard key={key} accent={accent}>
              <div className="flex items-center gap-2 mb-3">
                <Icon className={`w-4.5 h-4.5 ${ACCENT_TEXT[accent]}`} />
                <h2 className={`font-display text-lg ${ACCENT_TEXT[accent]}`}>{title}</h2>
              </div>
              {buckets[key].length === 0 ? (
                <p className="text-sm text-ink-400 font-body">No specific action needed in this category.</p>
              ) : (
                <ul className="space-y-2">
                  {buckets[key].map((rec, i) => (
                    <li key={i} className="text-sm text-ink-700 flex gap-2 font-body">
                      <span className={ACCENT_TEXT[accent]}>•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              )}
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
