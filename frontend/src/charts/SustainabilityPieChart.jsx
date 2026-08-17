import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const DEFAULT_COLORS = ["#1F6F5C", "#B9791F", "#4C7A46", "#B23B2E", "#A8721E", "#8B968E"];

export default function SustainabilityPieChart({ data, colors = DEFAULT_COLORS, height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={95}
          paddingAngle={3}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={colors[index % colors.length]} stroke="none" />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 12 }}
          labelStyle={{ color: "#16211C" }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#5C6B62" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}