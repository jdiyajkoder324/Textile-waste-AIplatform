import { useState, useEffect, useCallback } from "react";
import { FileText, FileSpreadsheet, Download, Loader2, Calendar } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import GlassCard from "../components/GlassCard";
import { LoadingState, EmptyState } from "../components/StatusStates";
import { generateReport, getReportHistory, downloadPastReport } from "../services/api";
import { downloadBlob } from "../utils/downloadBlob";

const REPORT_TYPES = [
  { key: "waste_classification", label: "Waste Classification", desc: "Material categories, condition, contamination, recyclability" },
  { key: "recycling", label: "Recycling", desc: "Best methods, sustainability & environmental impact scores" },
  { key: "sustainability", label: "Sustainability", desc: "Sustainability index, rating, waste diversion" },
  { key: "environmental_impact", label: "Environmental Impact", desc: "CO2, water, and landfill savings" },
  { key: "circular_economy", label: "Circular Economy", desc: "Circularity score, utilization, optimization" },
];

const TYPE_LABELS = Object.fromEntries(REPORT_TYPES.map((t) => [t.key, t.label]));

export default function ReportsCenter() {
  const [selectedType, setSelectedType] = useState("sustainability");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [generating, setGenerating] = useState(null); // format currently generating, or null

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const fetchHistory = useCallback(() => {
    setHistoryLoading(true);
    getReportHistory({ limit: 50 })
      .then((res) => setHistory(res.data.items))
      .finally(() => setHistoryLoading(false));
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const handleGenerate = async (format) => {
    setGenerating(format);
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const res = await generateReport(selectedType, format, params);
      const ext = format === "pdf" ? "pdf" : "xlsx";
      downloadBlob(res.data, `${selectedType}-report.${ext}`);
      fetchHistory();
    } catch (err) {
      alert(err.response?.data?.detail || "Report generation failed.");
    } finally {
      setGenerating(null);
    }
  };

  const handleDownloadPast = async (id, fileName) => {
    const res = await downloadPastReport(id);
    downloadBlob(res.data, fileName);
  };

  return (
    <div className="px-8 py-8 max-w-6xl mx-auto">
      <Breadcrumbs />

      <div className="mb-8">
        <h1 className="font-display text-3xl text-ink-900 tracking-tight">Reports Center</h1>
        <p className="font-body text-sm text-ink-500 mt-1.5">Generate and download platform reports as PDF or Excel.</p>
      </div>

      {/* Generate new report */}
      <GlassCard accent="teal" className="mb-8">
        <h2 className="font-display text-lg text-ink-900 mb-4">Generate a Report</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-5">
          {REPORT_TYPES.map(({ key, label, desc }) => (
            <button
              key={key}
              onClick={() => setSelectedType(key)}
              className={`text-left p-3.5 rounded-xl border transition-all duration-200 ${
                selectedType === key
                  ? "border-fiber-teal/40 bg-fiber-teal/[0.06] shadow-card"
                  : "border-ink-900/[0.07] hover:border-ink-900/15"
              }`}
            >
              <p className="text-sm font-semibold text-ink-900">{label}</p>
              <p className="text-xs text-ink-400 mt-1 leading-snug">{desc}</p>
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Calendar size={14} className="text-ink-400" />
            <input
              type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
              className="rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2 text-sm focus:outline-none focus:border-fiber-teal/60"
            />
            <span className="text-ink-400 text-sm">to</span>
            <input
              type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
              className="rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2 text-sm focus:outline-none focus:border-fiber-teal/60"
            />
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <button
              onClick={() => handleGenerate("pdf")}
              disabled={generating !== null}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-fiber-teal text-white font-body text-sm font-semibold
                         hover:bg-fiber-teal/90 disabled:opacity-50 transition-colors"
            >
              {generating === "pdf" ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
              {generating === "pdf" ? "Generating..." : "Download PDF"}
            </button>
            <button
              onClick={() => handleGenerate("excel")}
              disabled={generating !== null}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-fiber-amber text-white font-body text-sm font-semibold
                         hover:bg-fiber-amber/90 disabled:opacity-50 transition-colors"
            >
              {generating === "excel" ? <Loader2 size={16} className="animate-spin" /> : <FileSpreadsheet size={16} />}
              {generating === "excel" ? "Generating..." : "Download Excel"}
            </button>
          </div>
        </div>
      </GlassCard>

      {/* Report history */}
      <div>
        <h2 className="font-display text-lg text-ink-900 mb-4">Report History</h2>

        {historyLoading ? (
          <LoadingState label="Loading report history..." />
        ) : history.length === 0 ? (
          <EmptyState message="No reports generated yet. Create one above to see it here." />
        ) : (
          <div className="grid gap-2.5">
            {history.map((r) => (
              <div
                key={r.id}
                className="flex items-center gap-4 p-4 rounded-xl bg-paper-raised border border-ink-900/[0.06] shadow-card"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                  r.format === "pdf" ? "bg-fiber-teal/10 text-fiber-teal" : "bg-fiber-amber/10 text-fiber-amber"
                }`}>
                  {r.format === "pdf" ? <FileText size={18} /> : <FileSpreadsheet size={18} />}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-ink-900 font-body">{TYPE_LABELS[r.report_type] || r.report_type}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs font-mono text-ink-400 uppercase">{r.format}</span>
                    {(r.date_range_start || r.date_range_end) && (
                      <span className="text-xs text-ink-400">
                        {r.date_range_start || "…"} → {r.date_range_end || "…"}
                      </span>
                    )}
                    <span className="text-xs text-ink-300">{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleDownloadPast(r.id, r.file_name)}
                  className="shrink-0 p-2.5 rounded-lg border border-ink-900/[0.08] text-ink-500 hover:text-fiber-teal hover:border-fiber-teal/30 transition-colors"
                >
                  <Download size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}