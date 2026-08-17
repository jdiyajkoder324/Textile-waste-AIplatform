import React, { useState } from "react";
import { analyzeSustainability } from "../services/sustainabilityApi";
import GlassCard from "./GlassCard";
import { PlayCircle, Loader2 } from "lucide-react";

const MATERIALS = ["cotton", "polyester", "denim", "silk", "wool", "jute", "nylon", "linen", "rayon", "acrylic", "mixed"];

const inputClass =
  "w-full rounded-lg bg-paper border border-ink-900/[0.1] text-ink-900 placeholder:text-ink-400 px-3 py-2 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors";

export default function AnalyzeForm({ onResult }) {
  const [form, setForm] = useState({
    material_type: "cotton",
    weight_kg: 15,
    is_recycled: true,
    recycled_kg: 8,
    reused_kg: 2,
    recovered_kg: 1,
    landfilled_kg: 4,
    material_purity: 80,
    contamination_level: 15,
    damage_level: 20,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeSustainability(form);
      onResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || "Analysis failed. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <GlassCard className="mb-8" accent="teal">
      <h2 className="font-display text-lg text-ink-900 mb-4">Analyze a Waste Batch</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="text-xs text-ink-500 block mb-1.5">Material Type</label>
          <select
            value={form.material_type}
            onChange={(e) => handleChange("material_type", e.target.value)}
            className={inputClass}
          >
            {MATERIALS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-ink-500 block mb-1.5">Weight (kg)</label>
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={form.weight_kg}
            onChange={(e) => handleChange("weight_kg", parseFloat(e.target.value))}
            className={inputClass}
          />
        </div>

        <div>
          <label className="text-xs text-ink-500 block mb-1.5">Material Purity (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            value={form.material_purity}
            onChange={(e) => handleChange("material_purity", parseFloat(e.target.value))}
            className={inputClass}
          />
        </div>

        <div>
          <label className="text-xs text-ink-500 block mb-1.5">Contamination (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            value={form.contamination_level}
            onChange={(e) => handleChange("contamination_level", parseFloat(e.target.value))}
            className={inputClass}
          />
        </div>

        <div className="col-span-2 md:col-span-4 flex items-center justify-between mt-2">
          {error && <p className="text-sm text-fiber-rust">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="ml-auto flex items-center gap-2 px-5 py-2.5 rounded-lg bg-fiber-teal text-white font-semibold text-sm hover:opacity-90 transition disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
            {loading ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>
      </form>
    </GlassCard>
  );
}