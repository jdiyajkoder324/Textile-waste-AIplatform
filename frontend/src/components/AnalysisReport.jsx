import React, { useState } from "react";
import { FileDown, FileText, FileJson, FileSpreadsheet, Loader2 } from "lucide-react";
import { downloadReport } from "../services/api.js";

const FORMATS = [
  { key: "pdf", label: "PDF Report", icon: FileText },
  { key: "csv", label: "CSV Export", icon: FileSpreadsheet },
  { key: "json", label: "JSON Export", icon: FileJson },
];

export default function AnalysisReport({ imageId }) {
  const [loadingFormat, setLoadingFormat] = useState(null);

  const handleDownload = async (format) => {
    setLoadingFormat(format);
    try {
      await downloadReport(imageId, format);
    } finally {
      setLoadingFormat(null);
    }
  };

  if (!imageId) return null;

  return (
    <div className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileDown className="w-4 h-4 text-fiber-amber" />
        <h3 className="font-display text-lg text-ink-900">Download Analysis Report</h3>
      </div>
      <div className="flex flex-wrap gap-3">
        {FORMATS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => handleDownload(key)}
            disabled={loadingFormat !== null}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-fiber-teal/10 border border-fiber-teal/25 text-ink-800 hover:bg-fiber-teal/15 transition-colors disabled:opacity-50"
          >
            {loadingFormat === key ? (
              <Loader2 className="w-4 h-4 animate-spin text-fiber-amber" />
            ) : (
              <Icon className="w-4 h-4 text-fiber-amber" />
            )}
            <span className="text-sm">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}