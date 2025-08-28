import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import AnimatedCard from '../AnimatedCard';

interface LineChartCardProps {
  title: string;
  data: Array<{ label: string; value: number }>;
}

const LineChartCard: React.FC<LineChartCardProps> = ({ title, data }) => {
  return (
    <AnimatedCard title={title}>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </AnimatedCard>
  );
};

export default LineChartCard;
