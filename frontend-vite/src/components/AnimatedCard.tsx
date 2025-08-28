import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface AnimatedCardProps {
  children: ReactNode;
  title?: string;
}

const AnimatedCard: React.FC<AnimatedCardProps> = ({ children, title }) => {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }} className="bg-white p-4 rounded-2xl shadow-md">
      {title && <h3 className="font-semibold mb-2">{title}</h3>}
      {children}
    </motion.div>
  );
};

export default AnimatedCard;
