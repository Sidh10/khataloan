import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const THEME = {
  red: '#C0392B',
  blue: '#2E86AB',
  dark: '#1E1E38',
  text: '#ffffff',
  muted: '#A08060',
  grid: '#333333'
};

const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: THEME.text }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: THEME.dark,
      titleColor: THEME.text,
      bodyColor: THEME.text,
      borderColor: THEME.blue,
      borderWidth: 1
    }
  },
  scales: {
    x: {
      ticks: { color: THEME.muted },
      grid: { display: false }
    },
    y: {
      ticks: { color: THEME.muted },
      grid: { color: THEME.grid }
    }
  }
};

export default function CreditScorecard({ report }) {
  const { transactions = [] } = report || {};

  // Process data identically to Report.jsx but suited for Chart.js
  const { monthlyData, sourceDist } = useMemo(() => {
    const monthlyMap = {};
    const sources = { ledger: 0, voice: 0, upi: 0 };

    transactions.forEach(t => {
      // Data Source Distribution
      if (t.source) {
        sources[t.source.toLowerCase()] = (sources[t.source.toLowerCase()] || 0) + 1;
      }

      // Monthly Grouping
      const m = (t.date || "").slice(0, 7);
      if (!m) return;
      if (!monthlyMap[m]) monthlyMap[m] = { month: m, revenue: 0, expenses: 0 };
      
      if (t.type === "credit") {
        monthlyMap[m].revenue += t.amount;
      } else {
        monthlyMap[m].expenses += t.amount;
      }
    });

    const sortedMonths = Object.values(monthlyMap)
      .sort((a, b) => a.month.localeCompare(b.month))
      .slice(-12);

    return { monthlyData: sortedMonths, sourceDist: sources };
  }, [transactions]);

  // 1. Line Chart: 12-Month Revenue Trends
  const revenueLineData = {
    labels: monthlyData.map(d => d.month),
    datasets: [
      {
        label: 'Gross Revenue (₹)',
        data: monthlyData.map(d => d.revenue),
        borderColor: THEME.blue,
        backgroundColor: `${THEME.blue}80`,
        borderWidth: 2,
        pointBackgroundColor: THEME.text,
        tension: 0.3
      }
    ]
  };

  // 2. Bar Chart: Monthly Net Surplus
  const surplusBarData = {
    labels: monthlyData.map(d => d.month),
    datasets: [
      {
        label: 'Net Surplus (₹)',
        data: monthlyData.map(d => d.revenue - d.expenses),
        backgroundColor: monthlyData.map(d => 
          (d.revenue - d.expenses) >= 0 ? THEME.blue : THEME.red
        ),
        borderRadius: 4
      }
    ]
  };

  // 3. Doughnut Chart: Data Source Distribution
  const sourceDoughnutData = {
    labels: ['Handwritten Ledger', 'UPI Screenshots', 'Voice Notes'],
    datasets: [
      {
        data: [sourceDist.ledger || 0, sourceDist.upi || 0, sourceDist.voice || 0],
        backgroundColor: [
          THEME.blue,
          '#F5A623', // Gold, keeping palette balance
          THEME.red
        ],
        borderWidth: 0,
        hoverOffset: 4
      }
    ]
  };

  const doughnutOptions = {
    ...commonOptions,
    scales: {}, // Remove grid scales for doughnut
    cutout: '70%',
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => ` ${ctx.label}: ${ctx.raw} entries`
        }
      }
    }
  };

  if (!transactions.length) {
    return <div style={{ color: THEME.muted }}>No transaction data available for scorecard.</div>;
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '1.5rem',
      marginTop: '2rem'
    }}>
      {/* 12-Month Revenue */}
      <div style={{ background: THEME.dark, padding: '1.5rem', borderRadius: '8px', border: `1px solid ${THEME.grid}` }}>
        <h3 style={{ color: THEME.text, fontSize: '1rem', marginTop: 0, marginBottom: '1rem' }}>12-Month Revenue Trend</h3>
        <div style={{ height: '220px' }}>
          <Line data={revenueLineData} options={commonOptions} />
        </div>
      </div>

      {/* Monthly Net Surplus */}
      <div style={{ background: THEME.dark, padding: '1.5rem', borderRadius: '8px', border: `1px solid ${THEME.grid}` }}>
        <h3 style={{ color: THEME.text, fontSize: '1rem', marginTop: 0, marginBottom: '1rem' }}>Monthly Net Surplus</h3>
        <div style={{ height: '220px' }}>
          <Bar data={surplusBarData} options={commonOptions} />
        </div>
      </div>

      {/* Data Source Distribution */}
      <div style={{ background: THEME.dark, padding: '1.5rem', borderRadius: '8px', border: `1px solid ${THEME.grid}` }}>
        <h3 style={{ color: THEME.text, fontSize: '1rem', marginTop: 0, marginBottom: '1rem' }}>Verification Sources</h3>
        <div style={{ height: '220px', display: 'flex', justifyContent: 'center' }}>
          <Doughnut data={sourceDoughnutData} options={doughnutOptions} />
        </div>
      </div>
    </div>
  );
}
