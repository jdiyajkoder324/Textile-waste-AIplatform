import React from "react";
import WasteBarChart from "../charts/WasteBarChart.jsx";
import { Recycle, AlertTriangle, ShieldCheck } from "lucide-react";

const CATEGORY_STYLES = {
  Recyclable: "text-fiber-teal border-fiber-teal/30 bg-fiber-teal/10",
  Reusable: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10",
  Repairable: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10",
  Upcyclable: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10",
  Compostable: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10",
  "Hazardous Textile Waste": "text-fiber-rust border-fiber-rust/30 bg-fiber-rust/10",
};

export default function WasteClassification({ waste, image }) {
  if (!waste) return null;

  const badgeStyle = CATEGORY_STYLES[waste.waste_category] || "text-ink-700 border-ink-900/20 bg-ink-900/5";
  const isHazardous = waste.waste_category === "Hazardous Textile Waste";

  return (
    <div className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Recycle className="w-4 h-4 text-fiber-teal" />
        <h3 className="font-display text-lg text-ink-900">Waste Classification</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm font-medium ${badgeStyle}`}>
            {isHazardous ? <AlertTriangle className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            {waste.waste_category}
          </span>

          <dl className="mt-5 grid grid-cols-2 gap-y-2 text-sm">
            <dt className="text-ink-500">Condition</dt>
            <dd className="text-ink-900">{waste.waste_condition}</dd>
            <dt className="text-ink-500">Damage Level</dt>
            <dd className="text-ink-900">{waste.damage_level}</dd>
            <dt className="text-ink-500">Contamination</dt>
            <dd className="text-ink-900">{waste.contamination_percentage}%</dd>
            <dt className="text-ink-500">Recyclability</dt>
            <dd className="text-ink-900">{waste.recyclability_percentage}%</dd>
          </dl>

          <p className="mt-4 text-xs text-ink-600 leading-relaxed">
            <span className="text-ink-400">Disposal guidance: </span>
            {waste.disposal_method}
          </p>

          {image && (image.damage_detected || image.contamination_detected) && (
            <div className="mt-4 flex flex-wrap gap-2">
              {image.damage_detected && (
                <span className="text-[11px] px-2 py-1 rounded-md bg-fiber-rust/10 text-fiber-rust border border-fiber-rust/25">
                  Damage detected · {image.damage_regions?.length || 0} region(s)
                </span>
              )}
              {image.contamination_detected && (
                <span className="text-[11px] px-2 py-1 rounded-md bg-fiber-amber/10 text-fiber-amber border border-fiber-amber/25">
                  Contamination: {image.contamination_types?.join(", ") || "detected"}
                </span>
              )}
            </div>
          )}
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Category Confidence</p>
          <WasteBarChart categoryScores={waste.category_scores} />
        </div>
      </div>
    </div>
  );
}