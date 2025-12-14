/**
 * HostSelector component
 * Multi-select dropdown for choosing hosts to monitor
 */
import React, { useEffect, useState } from 'react';
import { apiService } from '../services/apiService';
import type { Host } from '../types';

interface HostSelectorProps {
  selectedHosts: string[];
  onChange: (hosts: string[]) => void;
}

export const HostSelector: React.FC<HostSelectorProps> = ({
  selectedHosts,
  onChange
}) => {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadHosts();
  }, []);

  const loadHosts = async () => {
    try {
      setLoading(true);
      const data = await apiService.getHosts();
      setHosts(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load hosts:', err);
      setError('Failed to load hosts');
    } finally {
      setLoading(false);
    }
  };

  const toggleHost = (hostname: string) => {
    if (selectedHosts.includes(hostname)) {
      onChange(selectedHosts.filter(h => h !== hostname));
    } else {
      onChange([...selectedHosts, hostname]);
    }
  };

  const selectAll = () => {
    onChange(hosts.map(h => h.hostname));
  };

  const clearAll = () => {
    onChange([]);
  };

  if (loading) return <div className="host-selector">Loading hosts...</div>;
  if (error) return <div className="host-selector error">{error}</div>;

  return (
    <div className="host-selector">
      <label className="selector-label">Hosts:</label>
      <div className="dropdown">
        <button
          className="dropdown-toggle"
          onClick={() => setIsOpen(!isOpen)}
        >
          {selectedHosts.length === 0
            ? 'Select hosts...'
            : `${selectedHosts.length} host${selectedHosts.length !== 1 ? 's' : ''} selected`}
        </button>

        {isOpen && (
          <div className="dropdown-menu">
            <div className="dropdown-actions">
              <button onClick={selectAll} className="action-button">
                Select All
              </button>
              <button onClick={clearAll} className="action-button">
                Clear All
              </button>
            </div>

            <div className="host-list">
              {hosts.map((host) => (
                <label key={host.id} className="host-item">
                  <input
                    type="checkbox"
                    checked={selectedHosts.includes(host.hostname)}
                    onChange={() => toggleHost(host.hostname)}
                  />
                  <span className="host-name">{host.display_name}</span>
                  <span className="host-hostname">({host.hostname})</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HostSelector;
