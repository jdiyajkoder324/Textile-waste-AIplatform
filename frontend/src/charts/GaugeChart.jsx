import React from "react";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";

const ACCENT_HEX = {
  teal: "#1F6F5C",
  amber: "#B9791F",
  moss: "#4C7A46",
  rust: "#B23B2E",
};

export default function GaugeChart({ value = 0, label = "", accent = "teal", height = 200 }) {
  const color = ACCENT_HEX[accent] || ACCENT_HEX.teal;
  const data = [{ name: label, value, fill: color }];

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={height}>
        <RadialBarChart innerRadius="70%" outerRadius="100%" data={data} startAngle={90} endAngle={-270}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background={{ fill: "rgba(21,37,32,0.06)" }} dataKey="value" cornerRadius={20} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="-mt-24 mb-8 text-center">
        <p className="text-3xl font-mono font-semibold text-ink-900">{value.toFixed(0)}</p>
        <p className="text-[11px] text-ink-400 uppercase tracking-[0.14em] mt-1 font-body">{label}</p>
      </div>
    </div>
  );
}