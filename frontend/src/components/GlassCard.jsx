import React from "react";

const ACCENT_BORDER = {
  teal: "hover:border-fiber-teal/35 hover:shadow-[0_16px_40px_-16px_rgba(31,111,92,0.35)]",
  amber: "hover:border-fiber-amber/35 hover:shadow-[0_16px_40px_-16px_rgba(185,121,31,0.3)]",
  moss: "hover:border-fiber-moss/35 hover:shadow-[0_16px_40px_-16px_rgba(76,122,70,0.3)]",
  rust: "hover:border-fiber-rust/35 hover:shadow-[0_16px_40px_-16px_rgba(178,59,46,0.3)]",
};

/**
 * GlassCard — light-mode surface card. White panel, soft shadow, top-edge
 * accent line, gentle lift + colored glow on hover.
 */
export default function GlassCard({ children, className = "", accent = "teal" }) {
  return (
    <div
      className={
        "relative rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card " +
        "p-5 transition-all duration-300 hover:-translate-y-0.5 " + (ACCENT_BORDER[accent] || ACCENT_BORDER.teal) + " " + className
      }
    >
      <div className="absolute top-0 left-5 right-5 h-[2px] rounded-full bg-ink-900/[0.06]" />
      {children}
    </div>
  );
}