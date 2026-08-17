import React from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function SustainabilityAreaChart({ data, dataKey = "value", xKey = "label", color = "#1F6F5C", height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.35} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(21,37,32,0.08)" />
        <XAxis dataKey={xKey} stroke="#5C6B62" fontSize={12} />
        <YAxis stroke="#5C6B62" fontSize={12} />
        <Tooltip
          contentStyle={{ background: "#FFFFFF", border: "1px solid rgba(21,37,32,0.1)", borderRadius: 12 }}
          labelStyle={{ color: "#16211C" }}
        />
        <Area type="monotone" dataKey={dataKey} stroke={color} fill="url(#areaFill)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}