import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Compass } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function LengthDistributionChart({ distribution = [] }) {
  if (!distribution || distribution.length === 0) {
    return null;
  }

  // Sort distribution by length
  const sorted = [...distribution].sort((a, b) => a.length - b.length);
  const labels = sorted.map(item => `${item.length} chars`);
  const counts = sorted.map(item => item.count);

  const data = {
    labels,
    datasets: [
      {
        label: 'Words',
        data: counts,
        fill: true,
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        borderColor: '#06b6d4',
        borderWidth: 2,
        tension: 0.35,
        pointBackgroundColor: '#06b6d4',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
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
          label: (context) => `${context.parsed.y} words of this length`,
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
        <Compass size={18} color="var(--accent-cyan)" />
        <span>Word Length Curve</span>
      </div>
      <div style={{ height: '240px', width: '100%', marginTop: '0.75rem' }}>
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
