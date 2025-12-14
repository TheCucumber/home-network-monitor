/**
 * TimeRangeSelector component
 * Button group for selecting time ranges
 */
import React from 'react';
import type { TimeRange, TimeRangeConfig } from '../types';

const TIME_RANGES: TimeRangeConfig[] = [
  { label: 'Last Hour', value: '1h', milliseconds: 60 * 60 * 1000 },
  { label: 'Last 6 Hours', value: '6h', milliseconds: 6 * 60 * 60 * 1000 },
  { label: 'Last 24 Hours', value: '24h', milliseconds: 24 * 60 * 60 * 1000 },
  { label: 'Last 7 Days', value: '7d', milliseconds: 7 * 24 * 60 * 60 * 1000 },
  { label: 'Last 30 Days', value: '30d', milliseconds: 30 * 24 * 60 * 60 * 1000 },
  { label: 'Last 90 Days', value: '90d', milliseconds: 90 * 24 * 60 * 60 * 1000 },
  { label: 'Last 120 Days', value: '120d', milliseconds: 120 * 24 * 60 * 60 * 1000 },
];

interface TimeRangeSelectorProps {
  selected: TimeRange;
  onChange: (range: TimeRange) => void;
}

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  selected,
  onChange
}) => {
  return (
    <div className="time-range-selector">
      <label className="selector-label">Time Range:</label>
      <div className="button-group">
        {TIME_RANGES.map((range) => (
          <button
            key={range.value}
            className={`range-button ${selected === range.value ? 'active' : ''}`}
            onClick={() => onChange(range.value)}
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TimeRangeSelector;
export { TIME_RANGES };
