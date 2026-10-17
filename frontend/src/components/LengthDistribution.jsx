import React from 'react';
import { Compass } from 'lucide-react';

export default function LengthDistribution({ distribution = [] }) {
  const maxCount = Math.max(...distribution.map(d => d.count), 1);

  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem' }}>
        <Compass size={18} color="var(--accent-cyan)" />
        <span>Word Length Distribution</span>
      </div>
      <div className="length-bars">
        {distribution.map((item, idx) => {
          const pct = Math.round((item.count / maxCount) * 100);
          return (
            <div key={idx} className="length-bar-row">
              <span className="length-label">{item.length} chars</span>
              <div className="freq-bar-bg">
                <div
                  className="freq-bar-fill"
                  style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #06b6d4, #6366f1)' }}
                />
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: '30px', textAlign: 'right' }}>
                {item.count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
