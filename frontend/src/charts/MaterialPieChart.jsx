import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const PALETTE = ["#B9791F", "#4C7A46", "#1F6F5C", "#B23B2E", "#8B968E"];

export default function MaterialPieChart({ fiberComposition = {} }) {
  const data = Object.entries(fiberComposition).map(([name, value]) => ({ name, value }));

  if (data.length === 0) {
    return <p className="text-sm text-ink-500">No composition data yet.</p>;
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={2}
            stroke="#FFFFFF"
            strokeWidth={2}
          >
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={PALETTE[index % PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 8, fontSize: 12, color: "#16211C" }}
            formatter={(value) => [`${value}%`, "Composition"]}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "#16211C" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}