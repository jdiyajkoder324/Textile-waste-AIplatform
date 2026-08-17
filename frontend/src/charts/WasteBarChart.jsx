import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const CATEGORY_COLORS = {
  Recyclable: "#1F6F5C",
  Reusable: "#4C7A46",
  Repairable: "#B9791F",
  Upcyclable: "#A8721E",
  Compostable: "#6B8F79",
  "Hazardous Textile Waste": "#B23B2E",
};

export default function WasteBarChart({ categoryScores = {} }) {
  const data = Object.entries(categoryScores)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return <p className="text-sm text-ink-500">No waste classification data yet.</p>;
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
          <XAxis type="number" domain={[0, 100]} tick={{ fill: "#16211C", fontSize: 11 }} />
          <YAxis type="category" dataKey="name" width={140} tick={{ fill: "#16211C", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 8, fontSize: 12, color: "#16211C" }}
            formatter={(value) => [`${value}%`, "Confidence"]}
            cursor={{ fill: "rgba(21,37,32,0.03)" }}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={CATEGORY_COLORS[entry.name] || "#4C7A46"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}