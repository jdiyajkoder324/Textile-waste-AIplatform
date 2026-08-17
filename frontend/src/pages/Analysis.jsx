import React from "react";
import { Link } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext.jsx";
import { getImagePreviewUrl } from "../services/api.js";
import MaterialPrediction from "../components/MaterialPrediction.jsx";
import WasteClassification from "../components/WasteClassification.jsx";
import RecyclingSuggestions from "../components/RecyclingSuggestions.jsx";
import AnalysisReport from "../components/AnalysisReport.jsx";
import { ImageOff, UploadCloud } from "lucide-react";

export default function Analysis() {
  const { currentAnalysis } = useAnalysis();

  if (!currentAnalysis) {
    return (
      <div className="min-h-screen bg-paper">
        <div className="max-w-3xl mx-auto px-6 py-24 text-center">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-ink-900/[0.03] border border-ink-900/10 flex items-center justify-center mb-4">
            <ImageOff className="w-7 h-7 text-ink-400" />
          </div>
          <h2 className="font-display text-2xl text-ink-900 mb-2">No analysis to show yet</h2>
          <p className="text-ink-600 mb-6">Upload a textile image to see material prediction, waste classification, and recycling guidance.</p>
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-fiber-amber text-white font-medium hover:opacity-90 transition-colors"
          >
            <UploadCloud className="w-4 h-4" /> Upload an image
          </Link>
        </div>
      </div>
    );
  }

  const { image_analysis, material_classification, waste_classification, recyclability_assessment, recycling_recommendation } = currentAnalysis;

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-5xl mx-auto px-6 py-10 space-y-6">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="w-full md:w-56 shrink-0">
            <div className="aspect-square rounded-2xl overflow-hidden bg-paper-raised border border-ink-900/10">
              <img
                src={getImagePreviewUrl(image_analysis.id)}
                alt={image_analysis.filename}
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <div className="flex-1">
            <p className="text-xs uppercase tracking-widest text-fiber-amber mb-2">Step 02 — Results</p>
            <h1 className="font-display text-3xl text-ink-900 mb-1 truncate">{image_analysis.filename}</h1>
            <div className="flex flex-wrap gap-4 text-sm text-ink-600 mt-3">
              <span>Texture: <span className="text-ink-900">{image_analysis.fabric_texture}</span></span>
              <span>Pattern: <span className="text-ink-900">{image_analysis.fabric_pattern}</span></span>
              <span>Quality Score: <span className="text-ink-900">{image_analysis.image_quality_score}/100</span></span>
              <span>Confidence: <span className="text-ink-900">{image_analysis.fabric_confidence_score}%</span></span>
            </div>
          </div>
        </div>

        <MaterialPrediction material={material_classification} />
        <WasteClassification waste={waste_classification} image={image_analysis} />
        <RecyclingSuggestions recommendation={recycling_recommendation} recyclability={recyclability_assessment} />
        <AnalysisReport imageId={image_analysis.id} />
      </div>
    </div>
  );
}