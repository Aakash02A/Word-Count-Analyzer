import React from 'react';

/**
 * Reusable page header with title, description, and optional action slot.
 */
export default function PageHeader({ icon, title, description, children }) {
  return (
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-title">
          {icon && <span className="page-header-icon">{icon}</span>}
          <h2>{title}</h2>
        </div>
        {description && <p className="page-header-desc">{description}</p>}
      </div>
      {children && <div className="page-header-actions">{children}</div>}
    </div>
  );
}
