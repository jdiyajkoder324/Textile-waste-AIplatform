import React from "react";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";

export default function SustainabilityMeter({ score = 0, label = "Sustainability Score", color = "#4C7A46" }) {
  const data = [{ name: label, value: score, fill: color }];

  return (
    <div className="w-full h-40 relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart innerRadius="70%" outerRadius="100%" data={data} startAngle={90} endAngle={-270}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background={{ fill: "rgba(21,37,32,0.06)" }} dataKey="value" cornerRadius={12} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-2xl font-semibold text-ink-900">{Math.round(score)}</span>
        <span className="text-[10px] uppercase tracking-wider text-ink-500">{label}</span>
      </div>
    </div>
  );
}