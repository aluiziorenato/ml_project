import React from 'react';
import { motion } from 'framer-motion';
import { Bell, Settings, User, LogOut } from 'lucide-react';

interface HeaderProps {
  title?: string;
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
  onSettingsClick?: () => void;
  onProfileClick?: () => void;
  onLogoutClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  title = "ML Project Dashboard",
  user = { name: "John Doe", email: "john@example.com" },
  onSettingsClick,
  onProfileClick,
  onLogoutClick
}) => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-40"
    >
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Left side - Logo and Title */}
        <div className="flex items-center gap-4">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-3"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">ML</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900 hidden sm:block">
              {title}
            </h1>
          </motion.div>
        </div>
        {/* ...existing code... */}
      </div>
    </motion.header>
  );
};

export default Header;
