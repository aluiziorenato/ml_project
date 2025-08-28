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
  }
  // ...existing code...
];

const Navigation: React.FC<NavigationProps> = ({ currentPath, onNavigate, collapsed, onToggleCollapse }) => {
  // ...existing code...
  return (
    <nav>
      {/* ...existing code... */}
    </nav>
  );
};

export default Navigation;
