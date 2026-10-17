import React from 'react';
import { Hash, Sparkles, AlignLeft, Activity, Cpu } from 'lucide-react';

export default function MetricsCards({ result }) {
  if (!result) return null;

  const varietyPct = result.total_tokens > 0 
    ? Math.round((result.unique_tokens / result.total_tokens) * 100)
    : 0;

  const isSpark = result.metadata.engine_used === 'pyspark';

  return (
    <div className="metrics-summary-grid">
      <div className="metric-card">
        <div className="metric-header">
          <span>Total Tokens</span>
          <Hash size={16} color="var(--primary)" />
        </div>
        <div className="metric-value">{result.total_tokens.toLocaleString()}</div>
        <div className="metric-sub">Processed word count</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Unique Words</span>
          <Sparkles size={16} color="var(--accent-cyan)" />
        </div>
        <div className="metric-value">{result.unique_tokens.toLocaleString()}</div>
        <div className="metric-sub">{varietyPct}% vocabulary variety</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Avg Word Length</span>
          <AlignLeft size={16} color="var(--accent-emerald)" />
        </div>
        <div className="metric-value">{result.average_word_length}</div>
        <div className="metric-sub">Characters per token</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Raw Characters</span>
          <Activity size={16} color="var(--accent-amber)" />
        </div>
        <div className="metric-value">{result.metadata.raw_character_count.toLocaleString()}</div>
        <div className="metric-sub">Includes whitespace & symbols</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Engine Used</span>
          <Cpu size={16} color={isSpark ? '#c084fc' : 'var(--primary)'} />
        </div>
        <div className="metric-value" style={{ fontSize: '1.25rem', color: isSpark ? '#c084fc' : 'var(--text-main)' }}>
          {isSpark ? 'Apache PySpark' : 'Python In-Memory'}
        </div>
        <div className="metric-sub">
          {result.metadata.execution_time_ms !== null ? `${result.metadata.execution_time_ms} ms` : 'Cached'}
          {result.metadata.spark_version ? ` • Spark ${result.metadata.spark_version}` : ''}
        </div>
      </div>
    </div>
  );
}
