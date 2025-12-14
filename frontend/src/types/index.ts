/**
 * TypeScript types for the Network Monitor application
 * These match the Pydantic models from the backend
 */

export interface PingResult {
  host: string;
  timestamp: number;  // Unix timestamp in milliseconds
  latency: number | null;  // Latency in ms, null for failures
  success: boolean;
  error?: string;
}

export interface Host {
  id: number;
  hostname: string;
  display_name: string;
  enabled: boolean;
  created_at?: number;
}

export interface HostStatus {
  id: number;
  hostname: string;
  display_name: string;
  enabled: boolean;
  last_ping: number | null;
  latency: number | null;
  success: boolean;
  last_24h_avg: number | null;
  uptime_24h: number | null;  // Percentage
}

export interface PingDataResponse {
  host: string;
  data: PingResult[];
  stats: {
    avg_latency: number | null;
    min_latency: number | null;
    max_latency: number | null;
    success_rate: number;
  };
}

export interface HostsResponse {
  hosts: Host[];
}

export interface CurrentStatusResponse {
  hosts: HostStatus[];
}

export interface HostCreate {
  hostname: string;
  display_name: string;
}

export type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | '120d';

export interface TimeRangeConfig {
  label: string;
  value: TimeRange;
  milliseconds: number;
}
