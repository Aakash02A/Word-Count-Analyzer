import React from 'react';
import { Smile, Meh, Frown, Info } from 'lucide-react';

export default function SentimentCard({ sentiment }) {
  if (!sentiment) return null;

  const isPositive = sentiment.label === 'positive';
  const isNegative = sentiment.label === 'negative';
  const isNeutral = sentiment.label === 'neutral';

  const badgeColor = isPositive 
    ? 'var(--accent-emerald)' 
    : isNegative 
    ? 'var(--accent-rose)' 
    : 'var(--accent-amber)';

  const SentimentIcon = isPositive ? Smile : isNegative ? Frown : Meh;

  // Map polarity (-1.0 to 1.0) to percentage (0% to 100%)
  const polarityPct = Math.round(((sentiment.polarity + 1) / 2) * 100);
  const subjectivityPct = Math.round(sentiment.subjectivity * 100);

  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <SentimentIcon size={18} color={badgeColor} />
          <span>Sentiment Analysis</span>
        </div>
        <span
          style={{
            fontSize: '0.75rem',
            padding: '0.2rem 0.6rem',
            borderRadius: '999px',
            backgroundColor: isPositive ? 'rgba(16, 185, 129, 0.15)' : isNegative ? 'rgba(244, 63, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)',
            color: badgeColor,
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            border: `1px solid ${badgeColor}40`,
          }}
        >
          {sentiment.label}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: '0.35rem' }}>
            <span style={{ color: 'var(--text-dim)' }}>Polarity Score:</span>
            <span style={{ fontFamily: 'monospace', fontWeight: 600, color: badgeColor }}>
              {sentiment.polarity > 0 ? `+${sentiment.polarity}` : sentiment.polarity}
            </span>
          </div>
          <div className="freq-bar-bg" style={{ position: 'relative' }}>
            {/* Center zero line */}
            <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '2px', background: 'rgba(255,255,255,0.2)' }} />
            <div
              className="freq-bar-fill"
              style={{
                width: `${polarityPct}%`,
                background: isPositive ? 'var(--accent-emerald)' : isNegative ? 'var(--accent-rose)' : 'var(--accent-amber)',
              }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            <span>Negative (-1.0)</span>
            <span>Neutral (0.0)</span>
            <span>Positive (+1.0)</span>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: '0.35rem' }}>
            <span style={{ color: 'var(--text-dim)' }}>Subjectivity Score:</span>
            <span style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--accent-cyan)' }}>
              {sentiment.subjectivity} ({subjectivityPct}%)
            </span>
          </div>
          <div className="freq-bar-bg">
            <div
              className="freq-bar-fill"
              style={{ width: `${subjectivityPct}%`, background: 'var(--accent-cyan)' }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            <span>Objective (0.0)</span>
            <span>Subjective (1.0)</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.02)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
          <Info size={14} style={{ flexShrink: 0 }} />
          <span>Calculated using TextBlob heuristics. Polarity estimates lexical tone.</span>
        </div>
      </div>
    </div>
  );
}
