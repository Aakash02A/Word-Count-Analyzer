import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { BarChart3 } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function WordFrequencyChart({ topWords = [] }) {
  if (!topWords || topWords.length === 0) {
    return null;
  }

  const labels = topWords.map(item => item.word);
  const dataCounts = topWords.map(item => item.count);

  const data = {
    labels,
    datasets: [
      {
        label: 'Occurrences',
        data: dataCounts,
        backgroundColor: 'rgba(99, 102, 241, 0.75)',
        hoverBackgroundColor: 'rgba(129, 140, 248, 0.95)',
        borderColor: '#6366f1',
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: (context) => `Frequency: ${context.parsed.y} (${topWords[context.dataIndex]?.percentage || 0}%)`,
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#94a3b8',
          font: {
            size: 11,
            family: "'Inter', sans-serif",
          },
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.06)',
        },
        ticks: {
          color: '#94a3b8',
          font: {
            size: 11,
            family: "'Inter', sans-serif",
          },
          precision: 0,
        },
      },
    },
  };

  return (
    <div className="table-card">
      <div className="section-title" style={{ fontSize: '1.1rem' }}>
        <BarChart3 size={18} color="var(--primary)" />
        <span>Top Words Visual Distribution</span>
      </div>
      <div style={{ height: '260px', width: '100%', marginTop: '0.75rem' }}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}
