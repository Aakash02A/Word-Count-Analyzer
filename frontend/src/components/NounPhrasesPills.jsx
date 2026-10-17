import React from 'react';
import { Tag } from 'lucide-react';

export default function NounPhrasesPills({ phrases = [] }) {
  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem' }}>
        <Tag size={18} color="var(--primary)" />
        <span>Extracted Noun Phrases ({phrases.length})</span>
      </div>

      {phrases.length > 0 ? (
        <div className="bigram-grid">
          {phrases.map((phrase, idx) => (
            <div
              key={idx}
              className="bigram-pill"
              style={{
                backgroundColor: 'rgba(6, 182, 212, 0.1)',
                borderColor: 'rgba(6, 182, 212, 0.25)',
                color: '#a5f3fc',
              }}
            >
              <span>{phrase}</span>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: 'var(--text-dim)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          No distinctive noun phrases detected in content.
        </p>
      )}
    </div>
  );
}
