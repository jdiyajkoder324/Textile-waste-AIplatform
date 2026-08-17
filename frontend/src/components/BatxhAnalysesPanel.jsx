import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAnalysesForBatch } from "../../services/api";

export default function BatchAnalysesPanel({ wasteBatchId }) {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getAnalysesForBatch(wasteBatchId)
      .then((res) => { if (!cancelled) setAnalyses(res.data); })
      .catch(() => { if (!cancelled) setAnalyses([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [wasteBatchId]);

  if (loading) {
    return <p className="font-body text-xs text-white/40">Loading analyses...</p>;
  }

  if (analyses.length === 0) {
    return <p className="font-body text-xs text-white/40">No analyses yet for this batch.</p>;
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-xs text-white/40 uppercase tracking-wide">
        {analyses.length} analysis{analyses.length > 1 ? "es" : ""}
      </p>
      {analyses.map((a) => (
        <button
          key={a.id}
          onClick={() => navigate(`/analysis/${a.id}`)}
          className="flex items-center justify-between px-3 py-2 rounded-lg bg-ink-950
                     border border-white/5 hover:border-fiber-teal/40 transition-colors text-left"
        >
          <div>
            <p className="font-body text-sm text-white">{a.material || "Pending"}</p>
            <p className="font-mono text-xs text-white/40">
              {new Date(a.created_at).toLocaleDateString()}
            </p>
          </div>
          {a.recyclability_score != null && (
            <span className="font-mono text-sm text-fiber-teal">
              {a.recyclability_score.toFixed(0)}%
            </span>
          )}
        </button>
      ))}
    </div>
  );
}