/**
 * StatusCard component
 * Display current status for a single host
 */
import React from 'react';
import type { HostStatus } from '../types';

interface StatusCardProps {
  status: HostStatus;
}

export const StatusCard: React.FC<StatusCardProps> = ({ status }) => {
  const formatTimestamp = (timestamp: number | null): string => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const formatLatency = (latency: number | null): string => {
    if (latency === null) return 'N/A';
    return `${latency.toFixed(2)}ms`;
  };

  const getStatusClass = (): string => {
    if (!status.success) return 'status-down';
    if (status.latency && status.latency > 100) return 'status-slow';
    return 'status-up';
  };

  return (
    <div className={`status-card ${getStatusClass()}`}>
      <div className="card-header">
        <h3 className="host-name">{status.display_name}</h3>
        <div className={`status-indicator ${status.success ? 'online' : 'offline'}`}>
          {status.success ? '●' : '○'}
        </div>
      </div>

      <div className="card-body">
        <div className="status-row">
          <span className="label">Host:</span>
          <span className="value">{status.hostname}</span>
        </div>

        <div className="status-row">
          <span className="label">Status:</span>
          <span className="value">{status.success ? 'Online' : 'Offline'}</span>
        </div>

        <div className="status-row">
          <span className="label">Current Latency:</span>
          <span className="value">{formatLatency(status.latency)}</span>
        </div>

        <div className="status-row">
          <span className="label">24h Avg Latency:</span>
          <span className="value">{formatLatency(status.last_24h_avg)}</span>
        </div>

        <div className="status-row">
          <span className="label">24h Uptime:</span>
          <span className="value">
            {status.uptime_24h !== null ? `${status.uptime_24h.toFixed(2)}%` : 'N/A'}
          </span>
        </div>

        <div className="status-row">
          <span className="label">Last Ping:</span>
          <span className="value">{formatTimestamp(status.last_ping)}</span>
        </div>
      </div>
    </div>
  );
};

export default StatusCard;
