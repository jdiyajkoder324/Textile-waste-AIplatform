import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function SustainabilityBarChart({ data, dataKey = "value", xKey = "label", color = "#4C7A46", height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(21,37,32,0.08)" />
        <XAxis dataKey={xKey} stroke="#5C6B62" fontSize={12} />
        <YAxis stroke="#5C6B62" fontSize={12} />
        <Tooltip
          contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 12 }}
          labelStyle={{ color: "#16211C" }}
        />
        <Bar dataKey={dataKey} fill={color} radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}