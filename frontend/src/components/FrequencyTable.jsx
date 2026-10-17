import React from 'react';
import { BarChart3 } from 'lucide-react';

export default function FrequencyTable({ topWords = [] }) {
  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem' }}>
        <BarChart3 size={18} color="var(--primary)" />
        <span>Word Frequency Ranking (Top {topWords.length})</span>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '40px' }}>#</th>
            <th>Word</th>
            <th style={{ width: '70px' }}>Count</th>
            <th>Frequency</th>
          </tr>
        </thead>
        <tbody>
          {topWords.map((item, idx) => (
            <tr key={idx}>
              <td style={{ color: 'var(--text-dim)', fontFamily: 'monospace' }}>{idx + 1}</td>
              <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{item.word}</td>
              <td style={{ fontFamily: 'monospace', color: '#c7d2fe' }}>{item.count}</td>
              <td>
                <div className="freq-bar-container">
                  <div className="freq-bar-bg">
                    <div
                      className="freq-bar-fill"
                      style={{ width: `${Math.min(100, item.percentage * 2.5)}%` }}
                    />
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: '45px', textAlign: 'right' }}>
                    {item.percentage}%
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
