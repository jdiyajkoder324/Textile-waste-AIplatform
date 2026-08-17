import React from "react";

export default function DashboardCard({ icon: Icon, label, value, sublabel, accent = "amber" }) {
  const accentClasses = {
    amber: "text-fiber-amber bg-fiber-amber/10 border-fiber-amber/25",
    moss: "text-fiber-moss bg-fiber-moss/10 border-fiber-moss/25",
    teal: "text-fiber-teal bg-fiber-teal/10 border-fiber-teal/25",
    rust: "text-fiber-rust bg-fiber-rust/10 border-fiber-rust/25",
  }[accent];

  return (
    <div className="card-panel p-5 flex items-start gap-4">
      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center shrink-0 ${accentClasses}`}>
        {Icon && <Icon className="w-5 h-5" />}
      </div>
      <div className="min-w-0">
        <p className="text-xs uppercase tracking-wider text-fiber-sand/50">{label}</p>
        <p className="font-display text-xl text-fiber-sand truncate mt-0.5">{value ?? "—"}</p>
        {sublabel && <p className="text-xs text-fiber-sand/40 mt-0.5">{sublabel}</p>}
      </div>
    </div>
  );
}
