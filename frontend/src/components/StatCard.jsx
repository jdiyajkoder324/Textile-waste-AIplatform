import React from "react";
import GlassCard from "./GlassCard";

const ACCENT_TEXT = {
  teal: "text-fiber-teal",
  amber: "text-fiber-amber",
  moss: "text-fiber-moss",
  rust: "text-fiber-rust",
};

const ACCENT_CHIP = {
  teal: "bg-fiber-teal/10 ring-fiber-teal/20",
  amber: "bg-fiber-amber/10 ring-fiber-amber/20",
  moss: "bg-fiber-moss/10 ring-fiber-moss/20",
  rust: "bg-fiber-rust/10 ring-fiber-rust/20",
};

export default function StatCard({ label, value, unit = "", icon = null, accent = "teal", subtext = "" }) {
  return (
    <GlassCard accent={accent} className="flex flex-col gap-3 min-w-[180px]">
      <div className="flex items-center justify-between">
        <span className="text-[11px] uppercase tracking-[0.14em] text-ink-500 font-body">{label}</span>
        {icon && (
          <div className={`h-9 w-9 rounded-xl flex items-center justify-center text-lg ring-1 ${ACCENT_CHIP[accent] || ACCENT_CHIP.teal}`}>
            {icon}
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className={`text-3xl font-mono font-semibold tracking-tight ${ACCENT_TEXT[accent] || ACCENT_TEXT.teal}`}>
          {value}
        </span>
        {unit && <span className="text-sm text-ink-400 font-body">{unit}</span>}
      </div>
      {subtext && <p className="text-xs text-ink-400 font-body">{subtext}</p>}
    </GlassCard>
  );
}