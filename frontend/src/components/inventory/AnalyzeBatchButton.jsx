import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadAndAnalyze } from "../../services/api";

export default function AnalyzeBatchButton({ batch }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const hasStoredImage = Boolean(batch.image_path || batch.image);

  const handleAnalyzeClick = () => {
    if (hasStoredImage) {
      // No direct "analyze from stored path" endpoint in the real /api/upload-image
      // flow, so we still need a file — trigger the picker either way.
      fileInputRef.current?.click();
    } else {
      fileInputRef.current?.click();
    }
  };

  const handleFileSelected = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setLoading(true);
    try {
      const res = await uploadAndAnalyze(file, batch.id);
      navigate(`/analysis/${res.data.image_analysis.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <button
        onClick={handleAnalyzeClick}
        disabled={loading}
        className="px-4 py-2 rounded-lg bg-fiber-teal text-ink-950 font-body text-sm font-semibold
                   hover:bg-fiber-teal/90 disabled:opacity-40 disabled:cursor-not-allowed
                   transition-colors"
      >
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileSelected}
      />

      {error && <p className="font-body text-xs text-fiber-rust">{error}</p>}
    </div>
  );
}