import React from 'react';

export const Card = ({ children, className = "", ...props }) => (
  <div className={`bg-white shadow-sm border border-gray-200 rounded-lg ${className}`} {...props}>
    {children}
  </div>
);

export const CardHeader = ({ children, className = "", ...props }) => (
  <div className={`px-4 py-3 border-b border-gray-200 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = "", ...props }) => (
  <h3 className={`text-lg font-semibold text-gray-900 ${className}`} {...props}>
    {children}
  </h3>
);

export const CardContent = ({ children, className = "", ...props }) => (
  <div className={`px-4 py-3 ${className}`} {...props}>
    {children}
  </div>
);