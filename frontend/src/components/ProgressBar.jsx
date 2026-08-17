import React from "react";

const COLOR_MAP = {
  teal: "bg-fiber-teal",
  amber: "bg-fiber-amber",
  moss: "bg-fiber-moss",
  rust: "bg-fiber-rust",
};

export default function ProgressBar({ label, value = 0, color = "teal" }) {
  const barColor = COLOR_MAP[color] || COLOR_MAP.teal;
  const clamped = Math.max(0, Math.min(value, 100));

  return (
    <div className="mb-5">
      <div className="flex justify-between mb-1.5">
        <span className="text-sm text-ink-600 font-body">{label}</span>
        <span className="text-sm font-mono font-semibold text-ink-900">{clamped.toFixed(1)}</span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-ink-900/[0.06] border border-ink-900/[0.06] overflow-hidden">
        <div
          className={`h-full rounded-full ${barColor} transition-all duration-700 ease-out`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}