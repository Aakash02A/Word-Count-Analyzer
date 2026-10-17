import React, { useState, useMemo } from 'react';
import { BarChart3, Search, ArrowUpDown } from 'lucide-react';

export default function FrequencyTable({ topWords = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('count-desc');

  const filteredAndSortedWords = useMemo(() => {
    let result = [...topWords];

    // Filter by search query
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      result = result.filter(item => item.word.toLowerCase().includes(term));
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'count-asc':
          return a.count - b.count || a.word.localeCompare(b.word);
        case 'alpha-asc':
          return a.word.localeCompare(b.word);
        case 'alpha-desc':
          return b.word.localeCompare(a.word);
        case 'length-desc':
          return b.word.length - a.word.length || b.count - a.count;
        case 'length-asc':
          return a.word.length - b.word.length || b.count - a.count;
        case 'count-desc':
        default:
          return b.count - a.count || a.word.localeCompare(b.word);
      }
    });

    return result;
  }, [topWords, searchTerm, sortBy]);

  return (
    <div className="table-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div className="section-title" style={{ fontSize: '1.1rem', margin: 0 }}>
          <BarChart3 size={18} color="var(--primary)" />
          <span>Word Frequency Ranking</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
          Showing {filteredAndSortedWords.length} of {topWords.length}
        </span>
      </div>

      {/* Interactive Table Toolbar */}
      <div className="table-toolbar">
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: '8px' }} />
          <input
            type="text"
            className="table-search-input"
            style={{ paddingLeft: '28px' }}
            placeholder="Search words..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <ArrowUpDown size={14} color="var(--text-dim)" />
          <select
            className="table-sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="count-desc">Frequency: High → Low</option>
            <option value="count-asc">Frequency: Low → High</option>
            <option value="alpha-asc">Word: A → Z</option>
            <option value="alpha-desc">Word: Z → A</option>
            <option value="length-desc">Length: Longest First</option>
            <option value="length-asc">Length: Shortest First</option>
          </select>
        </div>
      </div>

      {filteredAndSortedWords.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-dim)', fontSize: '0.875rem' }}>
          No matching words found for "{searchTerm}"
        </div>
      ) : (
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
            {filteredAndSortedWords.map((item, idx) => (
              <tr key={item.word}>
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
      )}
    </div>
  );
}
