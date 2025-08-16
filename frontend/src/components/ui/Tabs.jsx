import React from 'react';

export const Tabs = ({ children, value, onValueChange, className = "", ...props }) => (
  <div className={`w-full ${className}`} {...props}>
    {React.Children.map(children, child =>
      React.cloneElement(child, { activeTab: value, setActiveTab: onValueChange })
    )}
  </div>
);

export const TabsList = ({ children, className = "", activeTab, setActiveTab, ...props }) => (
  <div className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500 ${className}`} {...props}>
    {React.Children.map(children, child =>
      React.cloneElement(child, { activeTab, setActiveTab })
    )}
  </div>
);

export const TabsTrigger = ({ children, value, className = "", activeTab, setActiveTab, ...props }) => (
  <button
    className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
      activeTab === value
        ? 'bg-white text-gray-950 shadow-sm'
        : 'text-gray-600 hover:text-gray-900'
    } ${className}`}
    onClick={() => setActiveTab(value)}
    {...props}
  >
    {children}
  </button>
);

export const TabsContent = ({ children, value, className = "", activeTab, ...props }) => {
  if (activeTab !== value) return null;
  
  return (
    <div className={`mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 ${className}`} {...props}>
      {children}
    </div>
  );
};