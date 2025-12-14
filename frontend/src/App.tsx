/**
 * Main App component
 * Home Network Monitor Dashboard
 */
import React, { useState, useEffect } from 'react';
import { TimeRangeSelector } from './components/TimeRangeSelector';
import { HostSelector } from './components/HostSelector';
import { StatusCard } from './components/StatusCard';
import { PingChart } from './components/PingChart';
import { usePingData, useCurrentStatus } from './hooks/usePingData';
import type { TimeRange } from './types';
import './App.css';

function App() {
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [selectedHosts, setSelectedHosts] = useState<string[]>([]);

  // Fetch current status for all hosts
  const { data: statusData, loading: statusLoading } = useCurrentStatus();

  // Auto-select first host when data loads
  useEffect(() => {
    if (statusData && selectedHosts.length === 0) {
      const firstHost = statusData.hosts[0]?.hostname;
      if (firstHost) {
        setSelectedHosts([firstHost]);
      }
    }
  }, [statusData, selectedHosts.length]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Home Network Monitor</h1>
        <p className="subtitle">Real-time Network Latency Monitoring</p>
      </header>

      <main className="app-main">
        {/* Controls Section */}
        <section className="controls-section">
          <HostSelector
            selectedHosts={selectedHosts}
            onChange={setSelectedHosts}
          />
          <TimeRangeSelector
            selected={timeRange}
            onChange={setTimeRange}
          />
        </section>

        {/* Status Cards Section */}
        <section className="status-section">
          <h2>Current Status</h2>
          {statusLoading ? (
            <div className="loading">Loading status...</div>
          ) : (
            <div className="status-grid">
              {statusData?.hosts.map((status) => (
                <StatusCard key={status.id} status={status} />
              ))}
            </div>
          )}
        </section>

        {/* Charts Section */}
        <section className="charts-section">
          <h2>Latency History</h2>
          {selectedHosts.length === 0 ? (
            <div className="no-selection">
              <p>Please select at least one host to view its latency history</p>
            </div>
          ) : (
            <div className="charts-container">
              {selectedHosts.map((hostname) => (
                <ChartWrapper
                  key={hostname}
                  hostname={hostname}
                  timeRange={timeRange}
                />
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="app-footer">
        <p>Home Network Monitor &copy; 2024</p>
      </footer>
    </div>
  );
}

/**
 * Wrapper component for individual charts with data fetching
 */
interface ChartWrapperProps {
  hostname: string;
  timeRange: TimeRange;
}

const ChartWrapper: React.FC<ChartWrapperProps> = ({ hostname, timeRange }) => {
  const { data, loading, error } = usePingData(hostname, timeRange);

  if (loading) {
    return (
      <div className="chart-wrapper">
        <h3>{hostname}</h3>
        <div className="loading">Loading chart data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-wrapper">
        <h3>{hostname}</h3>
        <div className="error">Failed to load data: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="chart-wrapper">
      <h3>{hostname}</h3>
      {data && data.data.length > 0 ? (
        <>
          <PingChart data={data.data} hostname={hostname} />
          <div className="chart-stats">
            <div className="stat">
              <span className="stat-label">Avg Latency:</span>
              <span className="stat-value">
                {data.stats.avg_latency !== null
                  ? `${data.stats.avg_latency.toFixed(2)}ms`
                  : 'N/A'}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Min:</span>
              <span className="stat-value">
                {data.stats.min_latency !== null
                  ? `${data.stats.min_latency.toFixed(2)}ms`
                  : 'N/A'}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Max:</span>
              <span className="stat-value">
                {data.stats.max_latency !== null
                  ? `${data.stats.max_latency.toFixed(2)}ms`
                  : 'N/A'}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Success Rate:</span>
              <span className="stat-value">{data.stats.success_rate.toFixed(2)}%</span>
            </div>
          </div>
        </>
      ) : (
        <div className="chart-empty">
          <p>No data available for this time range</p>
        </div>
      )}
    </div>
  );
};

export default App;
