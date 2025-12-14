/**
 * API service for communicating with the backend
 */
import axios, { AxiosInstance } from 'axios';
import type {
  HostsResponse,
  CurrentStatusResponse,
  PingDataResponse,
  Host,
  HostCreate
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get all configured hosts
   */
  async getHosts(): Promise<Host[]> {
    const response = await this.client.get<HostsResponse>('/hosts');
    return response.data.hosts;
  }

  /**
   * Add a new host to monitor
   */
  async addHost(hostCreate: HostCreate): Promise<Host> {
    const response = await this.client.post<Host>('/hosts', hostCreate);
    return response.data;
  }

  /**
   * Delete a host and all its ping data
   */
  async deleteHost(hostId: number): Promise<void> {
    await this.client.delete(`/hosts/${hostId}`);
  }

  /**
   * Get current status for all hosts
   */
  async getCurrentStatus(): Promise<CurrentStatusResponse> {
    const response = await this.client.get<CurrentStatusResponse>('/current-status');
    return response.data;
  }

  /**
   * Get ping data for a specific host within a time range
   */
  async getPingData(
    hostname: string,
    start: number,
    end: number,
    limit: number = 1000
  ): Promise<PingDataResponse> {
    const response = await this.client.get<PingDataResponse>(`/ping-data/${encodeURIComponent(hostname)}`, {
      params: { start, end, limit }
    });
    return response.data;
  }

  /**
   * Manually trigger a ping for a specific host
   */
  async manualPing(hostname: string): Promise<any> {
    const response = await this.client.post(`/ping/${encodeURIComponent(hostname)}`);
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Admin: Trigger cleanup
   */
  async triggerCleanup(): Promise<any> {
    const response = await this.client.post('/admin/cleanup');
    return response.data;
  }

  /**
   * Admin: Trigger vacuum
   */
  async triggerVacuum(): Promise<any> {
    const response = await this.client.post('/admin/vacuum');
    return response.data;
  }

  /**
   * Admin: Get cleanup status
   */
  async getCleanupStatus(): Promise<any> {
    const response = await this.client.get('/admin/cleanup-status');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
