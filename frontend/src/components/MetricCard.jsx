import React from 'react'
import { motion } from 'framer-motion'

interface MetricCardProps {
  title: string
  value: string | number
  icon: string
  color: 'blue' | 'green' | 'purple' | 'orange'
}

const colorMap = {
  blue: ['text-blue-600', 'bg-blue-100'],
  green: ['text-green-600', 'bg-green-100'],
  purple: ['text-purple-600', 'bg-purple-100'],
  orange: ['text-orange-600', 'bg-orange-100']
} as const

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, color }) => {
  const [textColor, bgColor] = colorMap[color]

  return (
    <motion.div
      whileHover={{ scale: 1.05, zIndex: 10 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      style={{ transformOrigin: 'center' }}
      className="relative z-0 bg-white p-6 rounded-xl shadow-lg border border-gray-200"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className={`text-3xl font-bold ${textColor}`}>{value}</p>
        </div>
        <div className={`w-12 h-12 ${bgColor} rounded-lg flex items-center justify-center`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </motion.div>
  )
}

export default MetricCard
