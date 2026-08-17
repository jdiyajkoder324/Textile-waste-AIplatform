import React, { useState } from "react";
import { Link } from "react-router-dom";
import { jsPDF } from "jspdf";
import AnalyzeForm from "../components/AnalyzeForm";
import GlassCard from "../components/GlassCard";
import { EmptyState } from "../components/StatusStates";
import { ArrowLeft, FileText, Code2, Download, FileDown } from "lucide-react";

// Brand hex values (matched to the fiber-* token shadows used in GlassCard.jsx)
const BRAND = {
  ink: "#16211C",
  teal: "#1F6F5C",
  amber: "#B9791F",
  moss: "#4C7A46",
  rust: "#B23B2E",
  sand: "#FFFFFF",
  muted: "#5C6B62",
};

function downloadJSON(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function generatePDF(result) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 48;
  let y = 0;

  const ensureSpace = (needed) => {
    if (y + needed > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
  };

  // ---- Header band ----
  doc.setFillColor(BRAND.ink);
  doc.rect(0, 0, pageWidth, 90, "F");
  doc.setTextColor(BRAND.sand);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("TextileIntel", margin, 40);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(BRAND.teal);
  doc.text("SUSTAINABILITY INTELLIGENCE REPORT", margin, 58);
  doc.setTextColor(BRAND.muted);
  doc.setFontSize(9);
  doc.text(`Generated ${new Date().toLocaleString()}`, margin, 74);

  y = 120;

  const sectionTitle = (title, color = BRAND.teal) => {
    ensureSpace(30);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(color);
    doc.text(title, margin, y);
    doc.setDrawColor(color);
    doc.setLineWidth(1);
    doc.line(margin, y + 6, pageWidth - margin, y + 6);
    y += 26;
  };

  const row = (label, value) => {
    ensureSpace(20);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor(BRAND.muted);
    doc.text(label, margin, y);
    doc.setFont("helvetica", "bold");
    doc.setTextColor("#1A1A1A");
    doc.text(String(value), margin + 200, y);
    y += 18;
  };

  const paragraph = (text) => {
    const lines = doc.splitTextToSize(text, pageWidth - margin * 2);
    ensureSpace(lines.length * 14 + 6);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor("#1A1A1A");
    doc.text(lines, margin, y);
    y += lines.length * 14 + 10;
  };

  // ---- Batch overview ----
  sectionTitle("Batch Overview", BRAND.teal);
  row("Material Type", result.material_type ?? "—");
  row("Weight (kg)", result.weight_kg ?? "—");
  row("Sustainability Index", result.benchmark?.sustainability_index ?? "—");
  y += 8;

  // ---- Waste scores ----
  if (result.scores) {
    sectionTitle("Waste Scoring Breakdown", BRAND.amber);
    row("Category", result.scores.category ?? "—");
    row("Recyclability", `${result.scores.recyclability ?? "—"}`);
    row("Reuse", `${result.scores.reuse ?? "—"}`);
    row("Sustainability", `${result.scores.sustainability ?? "—"}`);
    row("Material Recovery", `${result.scores.recovery ?? "—"}`);
    row("Circularity", `${result.scores.circularity ?? "—"}`);
    y += 8;
  }

  // ---- Environmental impact ----
  if (result.environmental_report) {
    const env = result.environmental_report;
    sectionTitle("Environmental Impact", BRAND.moss);
    row("CO2 Saved", `${env.co2_saved ?? "—"} kg`);
    row("Water Saved", `${(env.water_saved ?? 0).toLocaleString()} L`);
    row("Landfill Reduced", `${env.landfill_saved ?? "—"} kg`);
    row("Energy Saved", `${env.energy_saved ?? "—"} kWh`);
    row("Rating", env.rating ?? "—");
    if (env.recommendation) {
      y += 4;
      paragraph(env.recommendation);
    }
    y += 8;
  }

  // ---- Circular economy ----
  if (result.circular_economy) {
    const ce = result.circular_economy;
    sectionTitle("Circular Economy", BRAND.rust);
    row("Circular Economy Score", `${ce.score ?? "—"}`);
    row("Utilization", `${ce.utilization ?? "—"}%`);
    row("Optimization", `${ce.optimization ?? "—"}%`);
    row("Category", ce.category ?? "—");
    y += 8;
  }

  // ---- Recommendations ----
  if (result.recommendations?.length) {
    sectionTitle("Recommendations", BRAND.teal);
    result.recommendations.forEach((rec) => {
      const lines = doc.splitTextToSize(`•  ${rec}`, pageWidth - margin * 2 - 10);
      ensureSpace(lines.length * 14 + 4);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10.5);
      doc.setTextColor("#1A1A1A");
      doc.text(lines, margin, y);
      y += lines.length * 14 + 6;
    });
  }

  // ---- Footer page numbers ----
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8.5);
    doc.setTextColor(BRAND.muted);
    doc.text(`Page ${i} of ${pageCount}`, pageWidth - margin, pageHeight - 24, { align: "right" });
    doc.text("TextileIntel — Sustainability Intelligence Platform", margin, pageHeight - 24);
  }

  doc.save(`sustainability-report-${result.material_type || "batch"}-${Date.now()}.pdf`);
}

export default function SustainabilityReportPage() {
  const [result, setResult] = useState(null);
  const [showJson, setShowJson] = useState(false);

  return (
    <div className="min-h-screen bg-paper p-6 md:p-10">
      <Link to="/sustainability" className="inline-flex items-center gap-1.5 text-xs text-ink-500 hover:text-ink-900 mb-6 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Sustainability Dashboard
      </Link>

      <div className="mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-fiber-teal/10 border border-fiber-teal/25 flex items-center justify-center">
          <FileText className="w-5 h-5 text-fiber-teal" />
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-fiber-teal font-mono mb-1">Sustainability Report</p>
          <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink-900">Full Analytics Summary</h1>
        </div>
      </div>

      <AnalyzeForm onResult={setResult} />

      {!result ? (
        <EmptyState message="Run an analysis above to generate a report." />
      ) : (
        <div className="space-y-6">
          <GlassCard accent="teal">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <h2 className="font-display text-lg text-fiber-sand">Analytics Summary</h2>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setShowJson((s) => !s)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-fiber-sand/5 border border-fiber-sand/15 text-fiber-sand text-sm hover:bg-fiber-sand/10 transition"
                >
                  <Code2 className="w-3.5 h-3.5" />
                  {showJson ? "Hide JSON" : "View JSON"}
                </button>
                <button
                  onClick={() =>
                    downloadJSON(result, `sustainability-report-${result.material_type}-${Date.now()}.json`)
                  }
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-fiber-teal text-ink-950 font-semibold text-sm hover:opacity-90 transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download JSON
                </button>
                <button
                  onClick={() => generatePDF(result)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-fiber-amber text-ink-950 font-semibold text-sm hover:opacity-90 transition"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  Download PDF
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-fiber-sand/50">Material</p>
                <p className="text-lg font-semibold text-fiber-sand capitalize">{result.material_type}</p>
              </div>
              <div>
                <p className="text-xs text-fiber-sand/50">Weight</p>
                <p className="text-lg font-semibold text-fiber-sand">{result.weight_kg} kg</p>
              </div>
              <div>
                <p className="text-xs text-fiber-sand/50">Circularity</p>
                <p className="text-lg font-semibold text-fiber-teal">{result.scores.circularity}</p>
              </div>
              <div>
                <p className="text-xs text-fiber-sand/50">Sustainability Index</p>
                <p className="text-lg font-semibold text-fiber-amber">{result.benchmark.sustainability_index}</p>
              </div>
            </div>
          </GlassCard>

          {showJson && (
            <GlassCard accent="moss">
              <pre className="text-xs text-fiber-sand/70 font-mono overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </GlassCard>
          )}
        </div>
      )}
    </div>
  );
}
