import React from "react";
import MaterialPieChart from "../charts/MaterialPieChart.jsx";
import { Layers, Sparkles } from "lucide-react";

export default function MaterialPrediction({ material }) {
  if (!material) return null;

  const {
    material_name, fabric_category, fiber_composition, blend_identification,
    fabric_quality, fabric_texture, pattern_information, material_confidence_percentage,
    sustainability_score,
  } = material;

  return (
    <div className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-4 h-4 text-fiber-amber" />
        <h3 className="font-display text-lg text-ink-900">Material Prediction</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p className="text-3xl font-display text-fiber-amber">{material_name}</p>
          <p className="text-sm text-ink-600 mt-1">{fabric_category}</p>
          <p className="text-xs text-ink-400 mt-1">{blend_identification}</p>

          <div className="mt-4 flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-fiber-moss" />
            <span className="text-xs text-ink-600">Confidence</span>
            <span className="font-mono text-sm text-fiber-moss">{material_confidence_percentage}%</span>
          </div>

          <dl className="mt-5 grid grid-cols-2 gap-y-2 text-sm">
            <dt className="text-ink-500">Fabric Quality</dt>
            <dd className="text-ink-900">{fabric_quality}</dd>
            <dt className="text-ink-500">Texture</dt>
            <dd className="text-ink-900">{fabric_texture}</dd>
            <dt className="text-ink-500">Pattern</dt>
            <dd className="text-ink-900">{pattern_information}</dd>
            <dt className="text-ink-500">Sustainability</dt>
            <dd className="text-ink-900">{sustainability_score}/100</dd>
          </dl>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Fiber Composition</p>
          <MaterialPieChart fiberComposition={fiber_composition} />
        </div>
      </div>
    </div>
  );
}