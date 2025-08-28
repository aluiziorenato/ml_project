import React from 'react';
import { motion } from 'framer-motion';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const colorClasses = {
  blue: "from-blue-500 to-blue-600",
  green: "from-green-500 to-green-600", 
  purple: "from-purple-500 to-purple-600",
  orange: "from-orange-500 to-orange-600",
  red: "from-red-500 to-red-600"
};

const KPICard: React.FC<KPICardProps> = ({ title, value, change, changeType, icon, color = "blue" }) => {
  const changeColor = changeType === 'positive' ? 'text-green-600' : 
                     changeType === 'negative' ? 'text-red-600' : 'text-gray-600';
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.5 }}
      className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-gray-600 mb-2">{title}</h4>
          <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
          {change && (
            <div className={`text-sm font-medium ${changeColor} flex items-center`}>
              <span className="mr-1">
                {changeType === 'positive' ? '\u2197' : changeType === 'negative' ? '\u2198' : '\u2192'}
              </span>
              {change}
            </div>
          )}
        </div>
        {icon && (
          <div className={`p-3 rounded-xl bg-gradient-to-r ${colorClasses[color]} text-white`}>
            <span className="text-2xl">{icon}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default KPICard;
