/**
 * PingChart component
 * Line chart displaying ping latency over time using Chart.js
 */
import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ChartOptions
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import type { PingResult } from '../types';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface PingChartProps {
  data: PingResult[];
  hostname: string;
}

export const PingChart: React.FC<PingChartProps> = ({ data, hostname }) => {
  const chartData = useMemo(() => {
    // Filter only successful pings for the chart
    const successfulPings = data.filter(d => d.success && d.latency !== null);

    return {
      datasets: [
        {
          label: `Latency (ms) - ${hostname}`,
          data: successfulPings.map(d => ({
            x: d.timestamp,
            y: d.latency
          })),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          pointRadius: 2,
          pointHoverRadius: 5,
        }
      ]
    };
  }, [data, hostname]);

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          title: (context) => {
            const date = new Date(context[0].parsed.x);
            return date.toLocaleString();
          },
          label: (context) => {
            const latency = context.parsed.y;
            return `Latency: ${latency.toFixed(2)}ms`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
          displayFormats: {
            minute: 'HH:mm',
            hour: 'MMM d, HH:mm',
            day: 'MMM d',
          }
        },
        title: {
          display: true,
          text: 'Time'
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Latency (ms)'
        }
      }
    }
  };

  if (data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No data available for {hostname}</p>
      </div>
    );
  }

  return (
    <div className="ping-chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default PingChart;
