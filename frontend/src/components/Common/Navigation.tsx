import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3, 
  Calendar, 
  Home, 
  Settings, 
  Brain,
  Activity,
  Database,
  Bell,
  Menu,
  X,
  ChevronDown
} from 'lucide-react';

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  badge?: number;
  children?: NavigationItem[];
}

interface NavigationProps {
  currentPath?: string;
  onNavigate?: (path: string) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    path: '/'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    path: '/analytics',
    children: [
      { id: 'predictions', label: 'Predictions', icon: Brain, path: '/analytics/predictions' },
      { id: 'models', label: 'Models', icon: Activity, path: '/analytics/models' },
      { id: 'optimization', label: 'Optimization', icon: Activity, path: '/analytics/optimization' }
    ]
  },
  {
    id: 'scheduler',
    label: 'Task Scheduler',
    icon: Calendar,
    path: '/scheduler',
    badge: 3,
    children: [
      { id: 'tasks', label: 'Task List', icon: Calendar, path: '/scheduler/tasks' },
      { id: 'calendar', label: 'Calendar', icon: Calendar, path: '/scheduler/calendar' }
    ]
  },
  {
    id: 'data',
    label: 'Data Management',
    icon: Database,
    path: '/data',
    children: [
      { id: 'campaigns', label: 'Campaigns', icon: Database, path: '/data/campaigns' },
      { id: 'storage', label: 'Storage', icon: Database, path: '/data/storage' }
    ]
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: Activity,
    path: '/monitoring',
    badge: 1
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/settings'
  }
];

const Navigation: React.FC<NavigationProps> = ({ 
  currentPath = '/',
  onNavigate,
  collapsed = false,
  onToggleCollapse
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const handleNavigate = (path: string) => {
    onNavigate?.(path);
    setMobileMenuOpen(false);
  };

  const isActive = (path: string) => {
    if (path === '/') return currentPath === '/';
    return currentPath.startsWith(path);
  };

  const renderNavigationItem = (item: NavigationItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);
    const active = isActive(item.path);

    return (
      <div key={item.id}>
        <motion.div
          whileHover={{ scale: collapsed && level === 0 ? 1.05 : 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`
            flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all
            ${level > 0 ? 'ml-6 pl-2' : ''}
            ${active ? 'bg-blue-100 text-blue-700 shadow-sm' : 'text-gray-700 hover:bg-gray-100'}
            ${collapsed && level === 0 ? 'justify-center' : ''}
          `}
          onClick={() => {
            if (hasChildren) {
              toggleExpanded(item.id);
            } else {
              handleNavigate(item.path);
            }
          }}
        >
          <item.icon className={`w-5 h-5 ${active ? 'text-blue-600' : 'text-gray-500'}`} />
          
          {!collapsed && (
            <>
              <span className="flex-1 text-sm font-medium">{item.label}</span>
              
              {item.badge && (
                <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                  {item.badge}
                </span>
              )}
              
              {hasChildren && (
                <ChevronDown
                  className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                />
              )}
            </>
          )}
        </motion.div>

        {/* Submenu */}
        <AnimatePresence>
          {hasChildren && isExpanded && !collapsed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="py-1">
                {item.children?.map(child => renderNavigationItem(child, level + 1))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tooltip for collapsed state */}
        {collapsed && level === 0 && (
          <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50">
            {item.label}
            {item.badge && (
              <span className="ml-2 px-1 py-0.5 bg-red-500 rounded-full text-xs">
                {item.badge}
              </span>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Desktop Navigation */}
      <motion.nav
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className={`
          hidden lg:flex flex-col bg-white border-r border-gray-200 h-screen sticky top-0 z-30
          transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {!collapsed && (
              <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
            )}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onToggleCollapse}
              className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </motion.button>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navigationItems.map(item => (
            <div key={item.id} className="relative group">
              {renderNavigationItem(item)}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          {!collapsed && (
            <div className="text-xs text-gray-500">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                System Online
              </div>
              <div>Last updated: {new Date().toLocaleTimeString()}</div>
            </div>
          )}
          
          {collapsed && (
            <div className="flex justify-center">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          )}
        </div>
      </motion.nav>

      {/* Mobile Navigation Toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 bg-white rounded-lg shadow-lg border border-gray-200"
        >
          {mobileMenuOpen ? (
            <X className="w-6 h-6 text-gray-600" />
          ) : (
            <Menu className="w-6 h-6 text-gray-600" />
          )}
        </motion.button>
      </div>

      {/* Mobile Navigation Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setMobileMenuOpen(false)}
          >
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="w-80 bg-white h-full shadow-xl"
              onClick={e => e.stopPropagation()}
            >
              {/* Mobile Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">Menu</h2>
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Mobile Navigation Items */}
              <div className="p-4 space-y-2 overflow-y-auto">
                {navigationItems.map(item => renderNavigationItem(item))}
              </div>

              {/* Mobile Footer */}
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
                <div className="text-xs text-gray-500">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    System Online
                  </div>
                  <div>Version 2.1.0</div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Actions Floating Button (Mobile) */}
      <div className="lg:hidden fixed bottom-6 right-6 z-40">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center"
        >
          <Bell className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            3
          </span>
        </motion.button>
      </div>
    </>
  );
};

export default Navigation;