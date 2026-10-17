import React from 'react';
import { Sparkles } from 'lucide-react';

export default function BigramPills({ bigrams = [] }) {
  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem' }}>
        <Sparkles size={18} color="var(--accent-emerald)" />
        <span>Frequent Bigrams (2-Word Phrases)</span>
      </div>
      {bigrams.length > 0 ? (
        <div className="bigram-grid">
          {bigrams.map((bg, idx) => (
            <div key={idx} className="bigram-pill">
              <span>{bg.bigram}</span>
              <span className="bigram-count">{bg.count}</span>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: 'var(--text-dim)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          Insufficient words to generate bigrams.
        </p>
      )}
    </div>
  );
}
