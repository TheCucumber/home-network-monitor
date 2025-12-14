/**
 * Hook for fetching ping data with SWR
 */
import useSWR from 'swr';
import { apiService } from '../services/apiService';
import type { TimeRange, PingDataResponse, CurrentStatusResponse } from '../types';
import { TIME_RANGES } from '../components/TimeRangeSelector';

/**
 * Get time range in milliseconds
 */
const getTimeRangeMs = (range: TimeRange): number => {
  const config = TIME_RANGES.find(r => r.value === range);
  return config?.milliseconds || 60 * 60 * 1000; // Default to 1 hour
};

/**
 * Hook to fetch ping data for a specific host and time range
 */
export const usePingData = (hostname: string | null, timeRange: TimeRange) => {
  const key = hostname ? ['ping-data', hostname, timeRange] : null;

  const fetcher = async ([_, host, range]: [string, string, TimeRange]) => {
    const end = Date.now();
    const start = end - getTimeRangeMs(range);

    return await apiService.getPingData(host, start, end);
  };

  const { data, error, isLoading, mutate } = useSWR<PingDataResponse>(
    key,
    fetcher,
    {
      refreshInterval: 60000, // Refresh every 60 seconds
      revalidateOnFocus: false,
      dedupingInterval: 5000,
    }
  );

  return {
    data,
    error,
    loading: isLoading,
    refetch: mutate
  };
};

/**
 * Hook to fetch current status for all hosts
 */
export const useCurrentStatus = () => {
  const fetcher = async () => {
    return await apiService.getCurrentStatus();
  };

  const { data, error, isLoading, mutate } = useSWR<CurrentStatusResponse>(
    'current-status',
    fetcher,
    {
      refreshInterval: 60000, // Refresh every 60 seconds
      revalidateOnFocus: true,
      dedupingInterval: 5000,
    }
  );

  return {
    data,
    error,
    loading: isLoading,
    refetch: mutate
  };
};

export default usePingData;
