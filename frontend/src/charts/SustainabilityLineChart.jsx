import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export default function SustainabilityLineChart({ data, lines, xKey = "label", height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(21,37,32,0.08)" />
        <XAxis dataKey={xKey} stroke="#5C6B62" fontSize={12} />
        <YAxis stroke="#5C6B62" fontSize={12} />
        <Tooltip
          contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 12 }}
          labelStyle={{ color: "#16211C" }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#5C6B62" }} />
        {lines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            name={line.name}
            stroke={line.color}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}