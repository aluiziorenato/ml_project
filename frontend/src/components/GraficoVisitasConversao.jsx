import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

export default function GraficoVisitasConversao({ visitas, conversao }) {
  // Une as séries num único array para o gráfico
  const data = (visitas || []).map((v) => {
    const convObj = (conversao || []).find((c) => c.date === v.date);
    return {
      date: v.date,
      visitas: v.value,
      conversao: convObj ? convObj.value : null
    };
  });

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={data}>
        <defs>
          <linearGradient id="colorVisitas" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.6} />
            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis yAxisId="left" />
        <YAxis
          yAxisId="right"
          orientation="right"
          tickFormatter={(val) => `${val}%`}
        />
        <Tooltip
          formatter={(value, name) => [
            name === "visitas" ? value : `${value}%`,
            name.charAt(0).toUpperCase() + name.slice(1)
          ]}
          labelFormatter={(label) => `Dia: ${label}`}
        />
        <Legend />
        <Area
          yAxisId="left"
          type="monotone"
          dataKey="visitas"
          stroke="#0ea5e9"
          fillOpacity={1}
          fill="url(#colorVisitas)"
          name="Visitas"
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="conversao"
          stroke="#f97316"
          dot={false}
          strokeWidth={2}
          name="Conversão (%)"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
