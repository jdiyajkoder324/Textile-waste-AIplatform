import React from "react";
import { useNavigate } from "react-router-dom";
import UploadImage from "../components/UploadImage.jsx";
import { uploadImage } from "../services/api.js";
import { useAnalysis } from "../context/AnalysisContext.jsx";

export default function Upload() {
  const { addAnalysis } = useAnalysis();
  const navigate = useNavigate();

  const handleAnalyzed = (result) => {
    addAnalysis(result);
    navigate("/analysis");
  };

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-widest text-fiber-amber mb-2">Step 01 — Intake</p>
          <h1 className="font-display text-3xl md:text-4xl text-ink-900">Upload textile images</h1>
          <p className="text-ink-600 mt-2 max-w-2xl">
            Drop in photos of fabric or garment waste. Each image runs through the full pipeline —
            texture &amp; color analysis, material classification, waste categorization, and a
            recycling recommendation — automatically.
          </p>
        </div>

        <UploadImage uploadFn={uploadImage} onAnalyzed={handleAnalyzed} />
      </div>
    </div>
  );
}