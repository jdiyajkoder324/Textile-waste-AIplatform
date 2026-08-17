import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Download, ArrowLeft } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import AuthedImage from "../components/AuthedImage";
import { getFullAnalysis, downloadAnalysisReport } from "../services/api";

function ScoreCard({ label, value, suffix = "%" }) {
  if (value == null) return null;
  return (
    <div className="p-4 rounded-xl bg-paper-raised border border-ink-900/[0.06] shadow-card">
      <p className="font-mono text-xs text-ink-400 uppercase tracking-wide">{label}</p>
      <p className="font-display text-2xl text-fiber-teal mt-1">
        {value.toFixed(0)}{suffix}
      </p>
    </div>
  );
}

export default function AnalysisDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getFullAnalysis(id)
      .then((res) => setData(res.data))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDownload = (format) => {
    setDownloading(true);
    downloadAnalysisReport(id, format).finally(() => setDownloading(false));
  };

  if (loading) {
    return (
      <div className="px-8 py-8 max-w-5xl mx-auto">
        <div className="h-96 rounded-2xl bg-ink-900/[0.04] animate-pulse" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="px-8 py-24 text-center">
        <p className="font-display text-xl text-ink-600">Analysis not found</p>
      </div>
    );
  }

  const { image_analysis, material_classification, waste_classification, recyclability_assessment, recycling_recommendation } = data;
  const { filename, status, created_at } = image_analysis;

  return (
    <div className="px-8 py-8 max-w-5xl mx-auto">
      <Breadcrumbs />

      <button
        onClick={() => navigate("/history")}
        className="flex items-center gap-2 font-body text-sm text-ink-600 hover:text-ink-900 mb-6 transition-colors"
      >
        <ArrowLeft size={16} /> Back to History
      </button>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl text-ink-900">{filename}</h1>
          <p className="font-mono text-xs text-ink-400 mt-1">
            {new Date(created_at).toLocaleString()} · {status}
          </p>
        </div>
        <button
          onClick={() => handleDownload("pdf")}
          disabled={downloading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-fiber-teal text-white
                     font-body text-sm font-semibold hover:bg-fiber-teal/90 disabled:opacity-40 transition-colors"
        >
          <Download size={16} />
          {downloading ? "Preparing..." : "Export PDF"}
        </button>
      </div>

      <div className="grid grid-cols-[280px_1fr] gap-8">
        <AuthedImage analysisId={image_analysis.id} className="w-full h-72 rounded-2xl object-cover border border-ink-900/[0.06]" />

        <div className="flex flex-col gap-6">
          {material_classification && (
            <div>
              <h2 className="font-display text-lg text-ink-900 mb-3">Material Recognition</h2>
              <div className="flex items-center gap-4">
                <span className="font-mono text-2xl text-fiber-teal">{material_classification.material_name}</span>
                <span className="font-body text-sm text-ink-500">
                  {material_classification.material_confidence_percentage?.toFixed(0)}% confidence
                </span>
              </div>
            </div>
          )}

          {waste_classification && (
            <div>
              <h2 className="font-display text-lg text-ink-900 mb-3">Waste Classification</h2>
              <span className="font-mono text-lg text-fiber-amber">{waste_classification.waste_category}</span>
            </div>
          )}
        </div>
      </div>

      {recyclability_assessment && (
        <div className="mt-8">
          <h2 className="font-display text-lg text-ink-900 mb-4">Recyclability</h2>
          <div className="grid grid-cols-3 gap-4">
            <ScoreCard label="Recyclability" value={recyclability_assessment.recyclability_percentage} />
            <ScoreCard label="Reuse Potential" value={recyclability_assessment.reuse_potential} />
            <ScoreCard label="Repairability" value={recyclability_assessment.repairability_score} />
          </div>
        </div>
      )}

      {recycling_recommendation && (
        <div className="mt-8 p-6 rounded-2xl bg-fiber-moss/5 border border-fiber-moss/20">
          <h2 className="font-display text-lg text-fiber-moss mb-2">
            Recommendation: {recycling_recommendation.best_recycling_method}
          </h2>
          {recycling_recommendation.reuse_suggestions?.length > 0 && (
            <ul className="mt-2 space-y-1">
              {recycling_recommendation.reuse_suggestions.map((s, i) => (
                <li key={i} className="font-body text-sm text-ink-700">• {s}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}